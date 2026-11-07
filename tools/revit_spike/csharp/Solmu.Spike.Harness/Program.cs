// FND-002 spike harness: verifies the .NET 10 <-> CPython stdio boundary WITHOUT Revit.
// Usage: dotnet run --project Solmu.Spike.Harness -- <python-exe> <path/to/spike_service.py>
// Exit code 0 = all checks passed.

using System.Runtime.InteropServices;
using Solmu.Spike.Ipc;

if (args.Length < 2)
{
    Console.Error.WriteLine("usage: Solmu.Spike.Harness <python-exe> <spike_service.py>");
    return 2;
}

var failures = 0;
void Check(string name, bool condition, string detail = "")
{
    Console.WriteLine($"{(condition ? "PASS" : "FAIL")}  {name}{(detail.Length > 0 ? "  " + detail : "")}");
    if (!condition) failures++;
}

var timeout = TimeSpan.FromSeconds(15);
using (var client = SpikeServiceClient.Start(args[0], args[1], timeout))
{
    var ping = client.Ping();
    Check("ping", ping.Ok, $"{ping.RoundTripMilliseconds} ms, {ping.Response?["summary"]?.ToJsonString()}");

    var report = SyntheticReport(roomCount: 500);
    var ack = client.SendProbeReport(report);
    Check("probe_report ack", ack.Ok, $"{ack.RoundTripMilliseconds} ms");
    Check("rooms_received == 500", (int?)ack.Response?["summary"]?["rooms_received"] == 500);
    Check("non-ASCII preserved", (string?)ack.Response?["summary"]?["client_runtime"] == report.Environment.Runtime);

    var bad = client.Send("explode", null);
    Check("unknown type -> error", !bad.Ok && bad.ErrorCode == "unknown_type", bad.ErrorCode ?? "");

    var again = client.Ping();
    Check("service alive after error", again.Ok);

    var sw = System.Diagnostics.Stopwatch.StartNew();
    var allOk = true;
    for (var i = 0; i < 100; i++) allOk &= client.Ping().Ok;
    Check("100 sequential pings", allOk, $"{sw.ElapsedMilliseconds} ms total");
}

try
{
    using var missing = SpikeServiceClient.Start("python-does-not-exist-xyz", args[1], timeout);
    Check("missing python -> exception", false);
}
catch (SpikeServiceException ex)
{
    Check("missing python -> SpikeServiceException", true, ex.Message);
}

Console.WriteLine(failures == 0 ? "ALL CHECKS PASSED" : $"{failures} CHECK(S) FAILED");
return failures == 0 ? 0 : 1;

static ProbeReport SyntheticReport(int roomCount)
{
    var env = new EnvironmentInfo(
        ProbeKind: "harness",
        RevitVersion: null, RevitBuild: null, RevitSubVersion: null,
        Runtime: RuntimeInformation.FrameworkDescription + " – synteettinen ÄÖÅ",
        OsDescription: RuntimeInformation.OSDescription,
        ProcessArchitecture: RuntimeInformation.ProcessArchitecture.ToString(),
        DocumentTitle: null, DocumentIsWorkshared: null,
        TimestampUtc: DateTime.UtcNow.ToString("O"));

    var rooms = Enumerable.Range(1, roomCount).Select(i => new RoomInfo(
        ElementId: i, UniqueId: Guid.NewGuid().ToString(), Number: (100 + i % 50).ToString(),
        Name: i % 7 == 0 ? null : "Huone " + i, ElementName: null, LevelId: 1, LevelName: "1. krs",
        IsPlaced: true, AreaInternal: 107.64, AreaSquareMeters: 10.0,
        VolumeInternal: 0, VolumeCubicMeters: 0, UnboundedHeightInternal: 8.2,
        BoundaryLoopCount: 1,
        BoundarySegments: [new BoundarySegmentInfo(1000 + i, "Walls", 10.0)],
        Error: null)).ToList();

    return new ProbeReport(env, "all", roomCount, false, rooms, [], 0, 0, 0,
        "autodesk.unit.unit:millimeters-1.0.1", "autodesk.unit.unit:squareMeters-1.0.1", 0, []);
}
