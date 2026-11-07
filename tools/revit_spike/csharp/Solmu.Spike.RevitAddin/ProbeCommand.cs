// FND-002 spike: READ-ONLY probe of a Revit 2027 document.
//
// - Opens no Transaction and modifies nothing (TransactionMode.ReadOnly).
// - Reads environment info, rooms (selected rooms, or all rooms up to a limit),
//   room boundaries, windows with host walls and from/to rooms, wall and
//   mechanical equipment counts, and project display units.
// - Writes the report as JSON to %LOCALAPPDATA%\Solmu\spike\.
// - If SOLMU_PYTHON and SOLMU_SPIKE_SERVICE are set, sends the report to the
//   CPython spike service over stdio and shows the round trip result.
//
// Every value here is reported raw so that the spike can VERIFY behaviour
// (units, unplaced rooms, zero volume, ...) instead of assuming it.

using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
using Autodesk.Revit.UI;
using Solmu.Spike.Ipc;

namespace Solmu.Spike.RevitAddin;

[Transaction(TransactionMode.ReadOnly)]
[Regeneration(RegenerationOption.Manual)]
public sealed class ProbeCommand : IExternalCommand
{
    private const int MaxRooms = 500;

    public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
    {
        var uiDoc = commandData.Application.ActiveUIDocument;
        if (uiDoc is null)
        {
            message = "No active document.";
            return Result.Failed;
        }

        var doc = uiDoc.Document;
        var app = commandData.Application.Application;
        var sw = Stopwatch.StartNew();
        var warnings = new List<string>();

        var env = new EnvironmentInfo(
            ProbeKind: "csharp-addin",
            RevitVersion: app.VersionNumber,
            RevitBuild: app.VersionBuild,
            RevitSubVersion: app.SubVersionNumber,
            Runtime: RuntimeInformation.FrameworkDescription,
            OsDescription: RuntimeInformation.OSDescription,
            ProcessArchitecture: RuntimeInformation.ProcessArchitecture.ToString(),
            DocumentTitle: doc.Title,
            DocumentIsWorkshared: doc.IsWorkshared,
            TimestampUtc: DateTime.UtcNow.ToString("O"));

        // --- Rooms: selection first, otherwise all rooms -------------------------------
        var selectedRooms = uiDoc.Selection.GetElementIds()
            .Select(doc.GetElement).OfType<Room>().ToList();
        var scope = selectedRooms.Count > 0 ? "selection" : "all";
        var roomsInScope = selectedRooms.Count > 0
            ? selectedRooms
            : new FilteredElementCollector(doc)
                .OfCategory(BuiltInCategory.OST_Rooms)
                .WhereElementIsNotElementType()
                .OfType<Room>()
                .ToList();

        var boundaryOptions = new SpatialElementBoundaryOptions
        {
            SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish,
        };
        var rooms = roomsInScope.Take(MaxRooms).Select(r => ReadRoom(doc, r, boundaryOptions)).ToList();
        if (roomsInScope.Count > MaxRooms)
            warnings.Add($"Only the first {MaxRooms} of {roomsInScope.Count} rooms were read.");

        // --- Windows, walls, mechanical equipment --------------------------------------
        var phase = doc.Phases.Size > 0 ? doc.Phases.get_Item(doc.Phases.Size - 1) : null;
        var windows = new FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_Windows)
            .WhereElementIsNotElementType()
            .OfType<FamilyInstance>()
            .Select(w => ReadWindow(doc, w, phase, warnings))
            .ToList();

        var walls = new FilteredElementCollector(doc).OfClass(typeof(Wall)).Cast<Wall>().ToList();
        var exteriorWalls = walls.Count(w => WallFunctionOf(doc, w) == "Exterior");

        // Radiators are commonly in Mechanical Equipment; this is only a count, the real
        // radiator family registry is ROOM-001.
        var mechanicalEquipment = new FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_MechanicalEquipment)
            .WhereElementIsNotElementType()
            .GetElementCount();

        var units = doc.GetUnits();
        var report = new ProbeReport(
            env, scope, roomsInScope.Count, roomsInScope.Count > MaxRooms, rooms, windows,
            walls.Count, exteriorWalls, mechanicalEquipment,
            units.GetFormatOptions(SpecTypeId.Length).GetUnitTypeId().TypeId,
            units.GetFormatOptions(SpecTypeId.Area).GetUnitTypeId().TypeId,
            sw.ElapsedMilliseconds, warnings);

        var outDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Solmu", "spike");
        Directory.CreateDirectory(outDir);
        var outFile = Path.Combine(outDir, $"probe-csharp-{DateTime.UtcNow:yyyyMMddTHHmmssZ}.json");
        File.WriteAllText(outFile, JsonSerializer.Serialize(report, new JsonSerializerOptions(SpikeJson.Options) { WriteIndented = true }));

        var ipcSummary = TryPythonRoundTrip(report, outDir);

        TaskDialog.Show("Solmu FND-002 probe",
            $"Revit {env.RevitVersion} ({env.RevitBuild})\n{env.Runtime}\n\n" +
            $"Rooms in scope ({scope}): {roomsInScope.Count}\n" +
            $"Windows: {windows.Count}, walls: {walls.Count} (exterior: {exteriorWalls})\n" +
            $"Mechanical equipment: {mechanicalEquipment}\n" +
            $"Read time: {report.ElapsedMilliseconds} ms\n\n" +
            $"Report: {outFile}\n\nPython IPC: {ipcSummary}");
        return Result.Succeeded;
    }

    private static RoomInfo ReadRoom(Document doc, Room room, SpatialElementBoundaryOptions options)
    {
        try
        {
            var loops = room.GetBoundarySegments(options) ?? [];
            var segments = loops.SelectMany(loop => loop).Select(s =>
            {
                var element = s.ElementId == ElementId.InvalidElementId ? null : doc.GetElement(s.ElementId);
                return new BoundarySegmentInfo(
                    element is null ? null : s.ElementId.Value,
                    element?.Category?.Name,
                    s.GetCurve().Length);
            }).ToList();

            var level = room.Level;
            return new RoomInfo(
                ElementId: room.Id.Value,
                UniqueId: room.UniqueId,
                Number: room.Number,
                // ROOM_NAME parameter, not Element.Name: verify in the spike which one Revit 2027 returns.
                Name: room.get_Parameter(BuiltInParameter.ROOM_NAME)?.AsString(),
                ElementName: room.Name,
                LevelId: level?.Id.Value,
                LevelName: level?.Name,
                IsPlaced: room.Location is not null,
                AreaInternal: room.Area,
                AreaSquareMeters: UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters),
                VolumeInternal: room.Volume,
                VolumeCubicMeters: UnitUtils.ConvertFromInternalUnits(room.Volume, UnitTypeId.CubicMeters),
                UnboundedHeightInternal: room.UnboundedHeight,
                BoundaryLoopCount: loops.Count,
                BoundarySegments: segments,
                Error: null);
        }
        catch (Exception ex)
        {
            // Record the failure instead of hiding the room: the spike must show edge cases.
            return new RoomInfo(room.Id.Value, room.UniqueId, null, null, null, null, null, false,
                0, null, 0, null, null, 0, [], $"{ex.GetType().Name}: {ex.Message}");
        }
    }

    private static WindowInfo ReadWindow(Document doc, FamilyInstance window, Phase? phase, List<string> warnings)
    {
        long? fromRoom = null, toRoom = null;
        try
        {
            if (phase is not null)
            {
                fromRoom = window.get_FromRoom(phase)?.Id.Value;
                toRoom = window.get_ToRoom(phase)?.Id.Value;
            }
        }
        catch (Exception ex)
        {
            warnings.Add($"Window {window.Id.Value}: from/to room failed: {ex.Message}");
        }

        var hostWall = window.Host as Wall;
        return new WindowInfo(
            window.Id.Value,
            window.Host?.Id.Value,
            hostWall is not null,
            hostWall is null ? null : WallFunctionOf(doc, hostWall),
            fromRoom,
            toRoom);
    }

    private static string? WallFunctionOf(Document doc, Wall wall)
    {
        var p = (doc.GetElement(wall.GetTypeId()) as WallType)?.get_Parameter(BuiltInParameter.FUNCTION_PARAM);
        return p is null || !p.HasValue ? null : ((WallFunction)p.AsInteger()).ToString();
    }

    private static string TryPythonRoundTrip(ProbeReport report, string outDir)
    {
        var python = Environment.GetEnvironmentVariable("SOLMU_PYTHON");
        var service = Environment.GetEnvironmentVariable("SOLMU_SPIKE_SERVICE");
        if (string.IsNullOrWhiteSpace(python) || string.IsNullOrWhiteSpace(service))
            return "not configured (set SOLMU_PYTHON and SOLMU_SPIKE_SERVICE)";
        try
        {
            using var client = SpikeServiceClient.Start(python, service, TimeSpan.FromSeconds(20), "--out-dir", outDir);
            var ping = client.Ping();
            if (!ping.Ok) return $"ping failed: {ping.ErrorCode} {ping.ErrorMessage}";
            var ack = client.SendProbeReport(report);
            return ack.Ok
                ? $"OK. ping {ping.RoundTripMilliseconds} ms, report {ack.RoundTripMilliseconds} ms, " +
                  $"python {(string?)ping.Response?["summary"]?["python_version"]}"
                : $"report failed: {ack.ErrorCode} {ack.ErrorMessage}";
        }
        catch (Exception ex)
        {
            return $"failed: {ex.Message}";
        }
    }
}
