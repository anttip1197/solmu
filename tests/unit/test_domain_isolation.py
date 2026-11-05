"""NFR-001: the domain package must be importable without Revit and with stdlib only.

The import runs in a fresh interpreter so that modules loaded by pytest or other tests
cannot mask a forbidden import.
"""

import json
import subprocess
import sys

FORBIDDEN_TOP_LEVEL_MODULES = {
    "Autodesk",
    "RevitAPI",
    "RevitAPIUI",
    "RevitServices",
    "clr",
    "pythonnet",
    "pyrevit",
    "System",
}

_PROBE = """
import json, sys
before = set(sys.modules)
import heating_ai.domain
loaded = sorted({name.split(".")[0] for name in set(sys.modules) - before})
print(json.dumps(loaded))
"""


def _modules_loaded_by_domain_import() -> set[str]:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(json.loads(result.stdout))


def test_domain_import_loads_no_revit_or_dotnet_modules() -> None:
    loaded = _modules_loaded_by_domain_import()
    assert loaded.isdisjoint(FORBIDDEN_TOP_LEVEL_MODULES), loaded & FORBIDDEN_TOP_LEVEL_MODULES


def test_domain_import_loads_only_stdlib_and_own_package() -> None:
    loaded = _modules_loaded_by_domain_import()
    allowed = set(sys.stdlib_module_names) | {"heating_ai"}
    assert loaded <= allowed, f"Non-stdlib modules imported by domain: {sorted(loaded - allowed)}"
