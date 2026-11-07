# -*- coding: utf-8 -*-
"""FND-002 spike: READ-ONLY Revit 2027 probe for pyRevit.

Runs on pyRevit's default IronPython 2.7.12 engine and on IronPython 3.4.2
(so: no f-strings, no type hints, no walrus). Opens no Transaction and modifies nothing.

Produces the same report shape as the C# probe (tools/revit_spike/csharp) so the
two integration options can be compared on the same model.
If SOLMU_PYTHON and SOLMU_SPIKE_SERVICE are set, the report is also sent to the
CPython spike service over stdio.
"""
from __future__ import print_function

import json
import os
import sys
import time
from datetime import datetime

import clr  # noqa: F401  (provided by pyRevit / IronPython)
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    ElementId,
    FilteredElementCollector,
    SpatialElementBoundaryLocation,
    SpatialElementBoundaryOptions,
    SpecTypeId,
    UnitTypeId,
    UnitUtils,
    Wall,
    WallFunction,
)
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB.Mechanical import Space
from System import AppDomain, Enum, Environment, Guid
from System.Diagnostics import Process, ProcessStartInfo
from System.Runtime.InteropServices import RuntimeInformation
from System.Text import UTF8Encoding

MAX_ROOMS = 500
PARAMETER_SAMPLE_COUNT = 10

uiapp = __revit__  # noqa: F821  (injected by pyRevit)
uidoc = uiapp.ActiveUIDocument
doc = uidoc.Document
app = uiapp.Application


def eid(element_id):
    if element_id is None or element_id == ElementId.InvalidElementId:
        return None
    return int(element_id.Value)


def wall_function(wall):
    wall_type = doc.GetElement(wall.GetTypeId())
    if wall_type is None:
        return None
    p = wall_type.get_Parameter(BuiltInParameter.FUNCTION_PARAM)
    if p is None or not p.HasValue:
        return None
    return str(Enum.ToObject(WallFunction, p.AsInteger()))


def read_room(room, options):
    try:
        loops = room.GetBoundarySegments(options) or []
        segments = []
        for loop in loops:
            for s in loop:
                element = None if s.ElementId == ElementId.InvalidElementId else doc.GetElement(s.ElementId)
                segments.append({
                    "element_id": eid(s.ElementId) if element is not None else None,
                    "element_category": element.Category.Name if element is not None and element.Category is not None else None,
                    "length_internal": s.GetCurve().Length,
                })
        level = room.Level
        return {
            "element_id": eid(room.Id),
            "unique_id": room.UniqueId,
            "number": room.Number,
            "name": room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(),
            "element_name": room.Name,
            "level_id": eid(level.Id) if level is not None else None,
            "level_name": level.Name if level is not None else None,
            "is_placed": room.Location is not None,
            "area_internal": room.Area,
            "area_square_meters": UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters),
            "volume_internal": room.Volume,
            "volume_cubic_meters": UnitUtils.ConvertFromInternalUnits(room.Volume, UnitTypeId.CubicMeters),
            "unbounded_height_internal": room.UnboundedHeight,
            "boundary_loop_count": len(loops),
            "boundary_segments": segments,
            "error": None,
        }
    except Exception as exc:  # record, do not hide
        return {"element_id": eid(room.Id), "unique_id": room.UniqueId, "error": "%s: %s" % (type(exc).__name__, exc)}


def read_parameters(element):
    result = []
    for p in element.Parameters:
        guid = None
        if p.IsShared:
            try:
                guid = str(p.GUID)
            except Exception:
                guid = None
        value = None
        if p.HasValue:
            value = p.AsValueString() or p.AsString()
        result.append({
            "name": p.Definition.Name if p.Definition is not None else "?",
            "storage_type": str(p.StorageType),
            "is_shared": p.IsShared,
            "shared_guid": guid,
            "value_string": value,
            "double_internal": p.AsDouble() if p.HasValue and str(p.StorageType) == "Double" else None,
        })
    return sorted(result, key=lambda r: r["name"])


def read_space(space, include_parameters):
    try:
        name_param = space.get_Parameter(BuiltInParameter.ROOM_NAME)
        return {
            "element_id": eid(space.Id),
            "unique_id": space.UniqueId,
            "number": space.Number,
            "name": name_param.AsString() if name_param is not None else None,
            "level_name": space.Level.Name if space.Level is not None else None,
            "room_id": eid(space.Room.Id) if space.Room is not None else None,
            "is_placed": space.Location is not None,
            "area_internal": space.Area,
            "volume_internal": space.Volume,
            "parameters": read_parameters(space) if include_parameters else None,
            "error": None,
        }
    except Exception as exc:
        return {"element_id": eid(space.Id), "unique_id": space.UniqueId, "error": "%s: %s" % (type(exc).__name__, exc)}


def read_equipment(instance, phase):
    space_id = None
    try:
        if phase is not None:
            sp = instance.get_Space(phase)
            space_id = eid(sp.Id) if sp is not None else None
    except Exception:
        space_id = None
    type_element = doc.GetElement(instance.GetTypeId())
    return {
        "element_id": eid(instance.Id),
        "family_name": instance.Symbol.FamilyName if instance.Symbol is not None else None,
        "type_name": type_element.Name if type_element is not None else None,
        "space_id": space_id,
        "instance_parameters": read_parameters(instance),
        "type_parameters": read_parameters(type_element) if type_element is not None else [],
    }


def read_window(window, phase, warnings):
    from_room = to_room = None
    try:
        if phase is not None:
            fr = window.get_FromRoom(phase)
            tr = window.get_ToRoom(phase)
            from_room = eid(fr.Id) if fr is not None else None
            to_room = eid(tr.Id) if tr is not None else None
    except Exception as exc:
        warnings.append("Window %s: from/to room failed: %s" % (eid(window.Id), exc))
    host = window.Host
    host_is_wall = isinstance(host, Wall)
    return {
        "element_id": eid(window.Id),
        "host_id": eid(host.Id) if host is not None else None,
        "host_is_wall": host_is_wall,
        "host_wall_function": wall_function(host) if host_is_wall else None,
        "from_room_id": from_room,
        "to_room_id": to_room,
    }


def send_to_python(report, out_dir):
    python = os.environ.get("SOLMU_PYTHON")
    service = os.environ.get("SOLMU_SPIKE_SERVICE")
    if not python or not service:
        return "not configured (set SOLMU_PYTHON and SOLMU_SPIKE_SERVICE)"
    psi = ProcessStartInfo()
    psi.FileName = python
    psi.Arguments = '-I "%s" --out-dir "%s"' % (service, out_dir)
    psi.UseShellExecute = False
    psi.CreateNoWindow = True
    psi.RedirectStandardInput = True
    psi.RedirectStandardOutput = True
    psi.RedirectStandardError = True
    psi.StandardOutputEncoding = UTF8Encoding(False)
    psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8"
    psi.EnvironmentVariables["PYTHONUTF8"] = "1"
    try:
        proc = Process.Start(psi)
    except Exception as exc:
        return "failed to start python: %s" % exc
    try:
        # Write UTF-8 bytes explicitly; StandardInputEncoding is not settable on all hosts.
        stdin = proc.StandardInput.BaseStream
        results = []
        for kind, payload in (("ping", None), ("probe_report", report)):
            msg = {"protocol": "solmu-spike", "version": 1, "id": str(Guid.NewGuid()), "type": kind}
            if payload is not None:
                msg["payload"] = payload
            data = UTF8Encoding(False).GetBytes(json.dumps(msg, ensure_ascii=True) + "\n")
            started = time.time()
            stdin.Write(data, 0, data.Length)
            stdin.Flush()
            line = proc.StandardOutput.ReadLine()  # spike: no timeout here, C# client has one
            elapsed_ms = int((time.time() - started) * 1000)
            if line is None:
                return "service exited: %s" % proc.StandardError.ReadToEnd()
            response = json.loads(line)
            if not response.get("ok"):
                return "%s failed: %s" % (kind, response.get("error"))
            results.append((kind, elapsed_ms, response.get("summary")))
        stdin.Close()
        proc.WaitForExit(10000)
        return "OK. " + ", ".join("%s %d ms" % (k, ms) for k, ms, _ in results) + \
            ", python %s" % results[0][2].get("python_version")
    finally:
        if not proc.HasExited:
            proc.Kill()


def main():
    started = time.time()
    warnings = []
    environment = {
        "probe_kind": "pyrevit",
        "revit_version": app.VersionNumber,
        "revit_build": app.VersionBuild,
        "revit_sub_version": app.SubVersionNumber,
        "runtime": RuntimeInformation.FrameworkDescription,
        "os_description": RuntimeInformation.OSDescription,
        "process_architecture": str(RuntimeInformation.ProcessArchitecture),
        "python_engine": sys.version,
        "document_title": doc.Title,
        "document_is_workshared": doc.IsWorkshared,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    selected = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
    selected = [e for e in selected if isinstance(e, Room)]
    scope = "selection" if selected else "all"
    rooms_in_scope = selected or [
        r for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
        if isinstance(r, Room)
    ]
    options = SpatialElementBoundaryOptions()
    options.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
    rooms = [read_room(r, options) for r in rooms_in_scope[:MAX_ROOMS]]
    if len(rooms_in_scope) > MAX_ROOMS:
        warnings.append("Only the first %d of %d rooms were read." % (MAX_ROOMS, len(rooms_in_scope)))

    phase = doc.Phases.get_Item(doc.Phases.Size - 1) if doc.Phases.Size > 0 else None
    windows = [
        read_window(w, phase, warnings)
        for w in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType()
    ]
    walls = list(FilteredElementCollector(doc).OfClass(Wall))
    exterior = len([w for w in walls if wall_function(w) == "Exterior"])
    equipment = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MechanicalEquipment)
                     .WhereElementIsNotElementType())
    mech = len(equipment)
    equipment_samples = [read_equipment(e, phase) for e in equipment[:PARAMETER_SAMPLE_COUNT]]
    all_spaces = [s for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces)
                  .WhereElementIsNotElementType() if isinstance(s, Space)]
    spaces = [read_space(s, i < PARAMETER_SAMPLE_COUNT) for i, s in enumerate(all_spaces[:MAX_ROOMS])]
    if len(all_spaces) > MAX_ROOMS:
        warnings.append("Only the first %d of %d spaces were read." % (MAX_ROOMS, len(all_spaces)))
    magicad = []
    for a in AppDomain.CurrentDomain.GetAssemblies():
        n = a.GetName()
        if n.Name is not None and "magicad" in n.Name.lower():
            magicad.append({"name": n.Name, "version": str(n.Version) if n.Version is not None else None, "location": None})
    magicad.sort(key=lambda x: x["name"])
    units = doc.GetUnits()

    report = {
        "environment": environment,
        "scope": scope,
        "rooms_total_in_scope": len(rooms_in_scope),
        "rooms_truncated": len(rooms_in_scope) > MAX_ROOMS,
        "rooms": rooms,
        "windows": windows,
        "wall_count": len(walls),
        "exterior_wall_count": exterior,
        "mechanical_equipment_count": mech,
        "length_display_unit": units.GetFormatOptions(SpecTypeId.Length).GetUnitTypeId().TypeId,
        "area_display_unit": units.GetFormatOptions(SpecTypeId.Area).GetUnitTypeId().TypeId,
        "elapsed_milliseconds": int((time.time() - started) * 1000),
        "warnings": warnings,
        "spaces_total": len(all_spaces),
        "spaces": spaces,
        "mechanical_equipment_samples": equipment_samples,
        "magi_cad_assemblies": magicad,
    }

    out_dir = os.path.join(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Solmu", "spike")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    out_file = os.path.join(out_dir, "probe-pyrevit-%s.json" % datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
    with open(out_file, "w") as f:
        f.write(json.dumps(report, indent=2, ensure_ascii=True))

    ipc = send_to_python(report, out_dir)

    print("Revit %s (%s)  %s" % (environment["revit_version"], environment["revit_build"], environment["runtime"]))
    print("Python engine: %s" % environment["python_engine"])
    print("Rooms in scope (%s): %d" % (scope, len(rooms_in_scope)))
    print("Windows: %d, walls: %d (exterior: %d), mechanical equipment: %d" % (len(windows), len(walls), exterior, mech))
    print("MEP spaces: %d, MagiCAD assemblies loaded: %d" % (len(all_spaces), len(magicad)))
    print("Read time: %d ms" % report["elapsed_milliseconds"])
    print("Report: %s" % out_file)
    print("Python IPC: %s" % ipc)
    for w in warnings:
        print("WARNING: %s" % w)


main()
