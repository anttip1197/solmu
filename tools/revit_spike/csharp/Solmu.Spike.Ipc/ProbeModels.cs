// FND-002 spike DTOs. NOT the production contract (that is FND-005).
// Plain serializable records only: no Revit API types may appear here.

using System.Text.Json;
using System.Text.Json.Serialization;

namespace Solmu.Spike.Ipc;

public sealed record EnvironmentInfo(
    string ProbeKind,              // "csharp-addin" | "pyrevit" | "harness"
    string? RevitVersion,          // Application.VersionNumber
    string? RevitBuild,            // Application.VersionBuild
    string? RevitSubVersion,       // Application.SubVersionNumber
    string Runtime,                // RuntimeInformation.FrameworkDescription
    string OsDescription,
    string ProcessArchitecture,
    string? DocumentTitle,
    bool? DocumentIsWorkshared,
    string TimestampUtc);

public sealed record BoundarySegmentInfo(
    long? ElementId,               // null when the boundary is a room separation / no element
    string? ElementCategory,
    double LengthInternal);        // Revit internal units (feet)

public sealed record RoomInfo(
    long ElementId,
    string UniqueId,
    string? Number,
    string? Name,                  // ROOM_NAME parameter
    string? ElementName,           // Element.Name (may differ: to be verified)
    long? LevelId,
    string? LevelName,
    bool IsPlaced,                 // Location != null
    double AreaInternal,           // square feet
    double? AreaSquareMeters,      // via UnitUtils + UnitTypeId.SquareMeters
    double VolumeInternal,         // cubic feet; 0 if volume computation is off
    double? VolumeCubicMeters,
    double? UnboundedHeightInternal,
    int BoundaryLoopCount,
    IReadOnlyList<BoundarySegmentInfo> BoundarySegments,
    string? Error);

public sealed record WindowInfo(
    long ElementId,
    long? HostId,
    bool HostIsWall,
    string? HostWallFunction,      // WallType "Function": Exterior/Interior/...
    long? FromRoomId,
    long? ToRoomId);

public sealed record ParameterInfo(
    string Name,
    string StorageType,            // Double/Integer/String/ElementId/None
    bool IsShared,
    string? SharedGuid,            // shared parameters (e.g. MagiCAD) are identified by GUID
    string? ValueString,           // AsValueString(): display units
    double? DoubleInternal);       // AsDouble(): internal units

public sealed record SpaceInfo(
    long ElementId,
    string UniqueId,
    string? Number,
    string? Name,
    string? LevelName,
    long? RoomId,                  // Space.Room: architectural room containing the space
    bool IsPlaced,
    double AreaInternal,
    double VolumeInternal,
    IReadOnlyList<ParameterInfo>? Parameters,  // only for the first few spaces
    string? Error);

public sealed record EquipmentSample(
    long ElementId,
    string? FamilyName,
    string? TypeName,
    long? SpaceId,                 // FamilyInstance.Space (last phase)
    IReadOnlyList<ParameterInfo> InstanceParameters,
    IReadOnlyList<ParameterInfo> TypeParameters);

public sealed record AssemblyInfo(string Name, string? Version, string? Location);

public sealed record ProbeReport(
    EnvironmentInfo Environment,
    string Scope,                  // "selection" | "all"
    int RoomsTotalInScope,
    bool RoomsTruncated,
    IReadOnlyList<RoomInfo> Rooms,
    IReadOnlyList<WindowInfo> Windows,
    int WallCount,
    int ExteriorWallCount,
    int MechanicalEquipmentCount,
    string LengthDisplayUnit,      // project display unit for length (ForgeTypeId)
    string AreaDisplayUnit,
    long ElapsedMilliseconds,
    IReadOnlyList<string> Warnings,
    int SpacesTotal,
    IReadOnlyList<SpaceInfo> Spaces,
    IReadOnlyList<EquipmentSample> MechanicalEquipmentSamples,
    IReadOnlyList<AssemblyInfo> MagiCadAssemblies);   // loaded assemblies whose name contains "magicad"

public static class SpikeJson
{
    public static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
        WriteIndented = false,
    };
}
