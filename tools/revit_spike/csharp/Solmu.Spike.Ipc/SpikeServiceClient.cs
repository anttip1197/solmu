// FND-002 spike: start the CPython spike service as a child process and talk to it
// with one JSON object per line over stdin/stdout. See spike_service.py for the protocol.

using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Solmu.Spike.Ipc;

public sealed record ServiceExchange(
    bool Ok,
    string? ErrorCode,
    string? ErrorMessage,
    JsonObject? Response,
    long RoundTripMilliseconds);

public sealed class SpikeServiceException(string message, Exception? inner = null)
    : Exception(message, inner);

public sealed class SpikeServiceClient : IDisposable
{
    private const string Protocol = "solmu-spike";
    private const int Version = 1;

    private readonly Process _process;
    private readonly StringBuilder _stderr = new();
    private readonly TimeSpan _timeout;

    private SpikeServiceClient(Process process, TimeSpan timeout)
    {
        _process = process;
        _timeout = timeout;
    }

    public string StandardError
    {
        get { lock (_stderr) { return _stderr.ToString(); } }
    }

    /// <summary>Start "pythonExe -I servicePath [args]". Paths come from configuration, never hard-coded.</summary>
    public static SpikeServiceClient Start(string pythonExe, string servicePath, TimeSpan timeout, params string[] serviceArgs)
    {
        if (!File.Exists(servicePath))
            throw new SpikeServiceException($"Spike service script not found: {servicePath}");

        var psi = new ProcessStartInfo
        {
            FileName = pythonExe,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardInputEncoding = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };
        psi.ArgumentList.Add("-I");
        psi.ArgumentList.Add(servicePath);
        foreach (var a in serviceArgs) psi.ArgumentList.Add(a);
        // Force UTF-8 regardless of the Windows console code page.
        psi.Environment["PYTHONIOENCODING"] = "utf-8";
        psi.Environment["PYTHONUTF8"] = "1";

        Process process;
        try
        {
            process = Process.Start(psi) ?? throw new SpikeServiceException("Process.Start returned null");
        }
        catch (Exception ex) when (ex is not SpikeServiceException)
        {
            throw new SpikeServiceException($"Could not start Python service '{pythonExe}': {ex.Message}", ex);
        }

        var client = new SpikeServiceClient(process, timeout);
        process.ErrorDataReceived += (_, e) =>
        {
            if (e.Data is null) return;
            lock (client._stderr) { client._stderr.AppendLine(e.Data); }
        };
        process.BeginErrorReadLine();
        return client;
    }

    public ServiceExchange Ping() => Send("ping", payload: null);

    public ServiceExchange SendProbeReport(ProbeReport report) =>
        Send("probe_report", JsonSerializer.SerializeToNode(report, SpikeJson.Options));

    public ServiceExchange Send(string type, JsonNode? payload)
    {
        var id = Guid.NewGuid().ToString();
        var request = new JsonObject
        {
            ["protocol"] = Protocol,
            ["version"] = Version,
            ["id"] = id,
            ["type"] = type,
        };
        if (payload is not null) request["payload"] = payload;

        var sw = Stopwatch.StartNew();
        string? line;
        try
        {
            _process.StandardInput.WriteLine(request.ToJsonString());
            _process.StandardInput.Flush();
            var readTask = _process.StandardOutput.ReadLineAsync();
            if (!readTask.Wait(_timeout))
                return Fail("timeout", $"No response within {_timeout.TotalSeconds:0.#} s", sw);
            line = readTask.Result;
        }
        catch (Exception ex)
        {
            return Fail("io_error", ex.Message, sw);
        }

        if (line is null)
            return Fail("service_exited", $"Service closed stdout. stderr: {StandardError}", sw);

        JsonObject? response;
        try
        {
            response = JsonNode.Parse(line) as JsonObject;
        }
        catch (JsonException ex)
        {
            return Fail("malformed_response", ex.Message, sw);
        }
        if (response is null) return Fail("malformed_response", "response is not an object", sw);
        if ((string?)response["id"] != id) return Fail("id_mismatch", $"expected id {id}", sw, response);

        var ok = response["ok"]?.GetValue<bool>() == true;
        return ok
            ? new ServiceExchange(true, null, null, response, sw.ElapsedMilliseconds)
            : new ServiceExchange(false, (string?)response["error"]?["code"], (string?)response["error"]?["message"], response, sw.ElapsedMilliseconds);
    }

    private static ServiceExchange Fail(string code, string message, Stopwatch sw, JsonObject? response = null) =>
        new(false, code, message, response, sw.ElapsedMilliseconds);

    public void Dispose()
    {
        try
        {
            if (!_process.HasExited)
            {
                _process.StandardInput.Close(); // service exits when stdin closes
                if (!_process.WaitForExit(_timeout))
                    _process.Kill(entireProcessTree: true);
            }
        }
        catch (InvalidOperationException)
        {
            // already exited
        }
        finally
        {
            _process.Dispose();
        }
    }
}
