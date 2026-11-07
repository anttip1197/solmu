"""FND-002: .NET 10 client <-> CPython spike service over stdio, without Revit.

Skipped when the .NET SDK is not installed. Builds and runs the C# harness, which
starts tools/revit_spike/python_service/spike_service.py with this interpreter.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CSHARP = ROOT / "tools" / "revit_spike" / "csharp"
SERVICE = ROOT / "tools" / "revit_spike" / "python_service" / "spike_service.py"

pytestmark = pytest.mark.skipif(shutil.which("dotnet") is None, reason=".NET SDK not installed")


def test_csharp_harness_round_trip() -> None:
    env = {"DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}
    proc = subprocess.run(
        ["dotnet", "run", "--project", str(CSHARP / "Solmu.Spike.Harness"), "-c", "Release", "--",
         sys.executable, str(SERVICE)],
        capture_output=True, text=True, timeout=600, check=False,
        env={**os.environ, **env},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ALL CHECKS PASSED" in proc.stdout
