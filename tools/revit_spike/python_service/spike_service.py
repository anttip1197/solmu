"""FND-002 spike: minimal Python service process for the Revit <-> Python boundary.

SPIKE CODE - NOT A PRODUCTION CONTRACT. The message format here exists only to test
whether a Revit-hosted client can start a CPython process and exchange JSON with it.
The real, versioned contracts are designed in FND-005.

Protocol (one JSON object per line, UTF-8, over stdin/stdout):

    request:  {"protocol": "solmu-spike", "version": 1, "id": "<str>",
               "type": "ping" | "probe_report", "payload": {...}}
    response: {"protocol": "solmu-spike", "version": 1, "id": "<str or null>",
               "ok": true, "type": "pong" | "ack", "summary": {...}}
           or {"protocol": "solmu-spike", "version": 1, "id": "<str or null>",
               "ok": false, "error": {"code": "<str>", "message": "<str>"}}

stdout is reserved for protocol messages. Diagnostics go to stderr.
The service exits when stdin is closed. Standard library only.
"""

from __future__ import annotations

import argparse
import io
import json
import platform
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, TextIO

PROTOCOL = "solmu-spike"
VERSION = 1
MAX_LINE_BYTES = 4 * 1024 * 1024  # a probe report of a few hundred rooms fits comfortably


class SpikeError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _response(request_id: str | None, **fields: Any) -> dict[str, Any]:
    return {"protocol": PROTOCOL, "version": VERSION, "id": request_id, **fields}


def _error(request_id: str | None, code: str, message: str) -> dict[str, Any]:
    return _response(request_id, ok=False, error={"code": code, "message": message})


def _summarize_probe(payload: dict[str, Any]) -> dict[str, Any]:
    rooms = payload.get("rooms")
    if not isinstance(rooms, list):
        raise SpikeError("invalid_payload", "probe_report.payload.rooms must be a list")
    environment = payload.get("environment")
    if not isinstance(environment, dict):
        raise SpikeError("invalid_payload", "probe_report.payload.environment must be an object")
    return {
        "rooms_received": len(rooms),
        "rooms_with_zero_area": sum(
            1 for r in rooms if isinstance(r, dict) and r.get("area_internal") in (0, 0.0)
        ),
        "client_revit_version": environment.get("revit_version"),
        "client_runtime": environment.get("runtime"),
    }


def handle_line(line: str, out_dir: Path | None = None) -> dict[str, Any]:
    """Process one request line and return the response object. Never raises."""
    request_id: str | None = None
    try:
        if len(line.encode("utf-8")) > MAX_LINE_BYTES:
            raise SpikeError("too_large", f"message exceeds {MAX_LINE_BYTES} bytes")
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SpikeError("malformed_json", str(exc)) from exc
        if not isinstance(message, dict):
            raise SpikeError("invalid_envelope", "message must be a JSON object")

        raw_id = message.get("id")
        request_id = raw_id if isinstance(raw_id, str) else None
        if message.get("protocol") != PROTOCOL:
            raise SpikeError("unsupported_protocol", f"expected protocol {PROTOCOL!r}")
        if message.get("version") != VERSION:
            raise SpikeError("unsupported_version", f"expected version {VERSION}")
        if request_id is None or not request_id:
            raise SpikeError("invalid_envelope", "id must be a non-empty string")

        kind = message.get("type")
        if kind == "ping":
            return _response(
                request_id,
                ok=True,
                type="pong",
                summary={
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation(),
                    "platform": platform.platform(),
                },
            )
        if kind == "probe_report":
            payload = message.get("payload")
            if not isinstance(payload, dict):
                raise SpikeError("invalid_payload", "payload must be an object")
            summary = _summarize_probe(payload)
            if out_dir is not None:
                out_dir.mkdir(parents=True, exist_ok=True)
                target = out_dir / f"probe-report-{_safe_name(request_id)}.json"
                target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), "utf-8")
                summary["saved_to"] = str(target)
            return _response(request_id, ok=True, type="ack", summary=summary)
        raise SpikeError("unknown_type", f"unknown message type: {kind!r}")
    except SpikeError as exc:
        return _error(request_id, exc.code, exc.message)
    except Exception as exc:  # spike: report, never crash the loop
        return _error(request_id, "internal_error", f"{type(exc).__name__}: {exc}")


def _safe_name(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in text)[:64]


def serve(lines: Iterable[str], out: TextIO, out_dir: Path | None = None) -> int:
    handled = 0
    for raw in lines:
        line = raw.rstrip("\r\n")
        if not line.strip():
            continue
        response = handle_line(line, out_dir)
        out.write(json.dumps(response, ensure_ascii=False) + "\n")
        out.flush()
        handled += 1
    return handled


def _stdin_lines() -> Iterator[str]:
    stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", newline="")
    yield from stream


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", type=Path, help="save received probe reports here")
    args = parser.parse_args(argv)

    stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    print(f"spike_service started, python {platform.python_version()}", file=sys.stderr)
    handled = serve(_stdin_lines(), stdout, args.out_dir)
    print(f"spike_service stopping, handled {handled} message(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
