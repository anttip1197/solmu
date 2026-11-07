"""FND-002 spike service: stdio JSON-lines behaviour, tested without Revit.

These tests exercise the Python side of the spike boundary in a real child process,
the same way the Revit-hosted client will start it.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SERVICE = Path(__file__).resolve().parents[2] / "tools" / "revit_spike" / "python_service" / "spike_service.py"


def _request(kind: str, request_id: str = "r1", payload: object | None = None, **overrides: object) -> str:
    message: dict[str, object] = {"protocol": "solmu-spike", "version": 1, "id": request_id, "type": kind}
    if payload is not None:
        message["payload"] = payload
    message.update(overrides)
    return json.dumps(message)


def _run(*lines: str, extra_args: tuple[str, ...] = ()) -> tuple[list[dict], subprocess.CompletedProcess[bytes]]:
    stdin = ("\n".join(lines) + "\n").encode("utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", str(SERVICE), *extra_args],
        input=stdin,
        capture_output=True,
        timeout=30,
        check=False,
    )
    responses = [json.loads(line) for line in proc.stdout.decode("utf-8").splitlines() if line.strip()]
    return responses, proc


def _probe_payload(rooms: list[dict]) -> dict:
    return {"environment": {"revit_version": "2027", "runtime": ".NET 10.0.0"}, "rooms": rooms}


def test_ping_returns_python_runtime_info() -> None:
    (response,), proc = _run(_request("ping"))
    assert proc.returncode == 0
    assert response["ok"] is True
    assert response["type"] == "pong"
    assert response["id"] == "r1"
    assert response["summary"]["python_implementation"] == "CPython"


def test_probe_report_is_acknowledged_and_summarized() -> None:
    rooms = [
        {"element_id": 1, "number": "101", "area_internal": 120.5},
        {"element_id": 2, "number": "101", "area_internal": 0.0},  # duplicate number, unenclosed
    ]
    (response,), _ = _run(_request("probe_report", payload=_probe_payload(rooms)))
    assert response["ok"] is True
    assert response["type"] == "ack"
    assert response["summary"]["rooms_received"] == 2
    assert response["summary"]["rooms_with_zero_area"] == 1
    assert response["summary"]["client_revit_version"] == "2027"


def test_probe_report_can_be_saved(tmp_path: Path) -> None:
    payload = _probe_payload([{"element_id": 1, "name": "Olohuone ÄÖ", "area_internal": 10.0}])
    (response,), _ = _run(_request("probe_report", "abc/../x", payload), extra_args=("--out-dir", str(tmp_path)))
    saved = Path(response["summary"]["saved_to"])
    assert saved.parent == tmp_path  # request id cannot escape the output directory
    assert json.loads(saved.read_text("utf-8")) == payload


def test_non_ascii_round_trips_as_utf8() -> None:
    (response,), _ = _run(_request("ping", request_id="pyyntö-ä"))
    assert response["id"] == "pyyntö-ä"


@pytest.mark.parametrize(
    ("line", "code"),
    [
        ("{not json", "malformed_json"),
        ("[1, 2]", "invalid_envelope"),
        (_request("ping", protocol="other"), "unsupported_protocol"),
        (_request("ping", version=2), "unsupported_version"),
        (_request("ping", request_id=""), "invalid_envelope"),
        (_request("explode"), "unknown_type"),
        (_request("probe_report"), "invalid_payload"),
        (_request("probe_report", payload={"rooms": "x", "environment": {}}), "invalid_payload"),
        (_request("probe_report", payload={"rooms": []}), "invalid_payload"),
    ],
)
def test_invalid_messages_return_errors(line: str, code: str) -> None:
    (response,), proc = _run(line)
    assert proc.returncode == 0
    assert response["ok"] is False
    assert response["error"]["code"] == code


def test_service_keeps_running_after_an_error() -> None:
    responses, proc = _run("{broken", _request("ping", request_id="after"))
    assert [r["ok"] for r in responses] == [False, True]
    assert responses[1]["id"] == "after"
    assert proc.returncode == 0


def test_blank_lines_are_ignored_and_stdout_has_only_protocol() -> None:
    responses, proc = _run("", _request("ping"), "   ")
    assert len(responses) == 1
    assert b"spike_service started" in proc.stderr
    assert b"spike_service started" not in proc.stdout


def test_oversized_message_is_rejected() -> None:
    big = _request("probe_report", payload=_probe_payload([{"pad": "x" * (4 * 1024 * 1024)}]))
    (response,), _ = _run(big)
    assert response["error"]["code"] == "too_large"
