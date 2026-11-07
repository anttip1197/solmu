"""FND-004 / NFR-003: repository hygiene check."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "check_repo_hygiene.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_repo_hygiene", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses need the module registered
    spec.loader.exec_module(module)
    return module


hygiene = _load()


def _write(root: Path, rel: str, content: str | bytes) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return rel


def _reasons(root: Path, *paths: str) -> list[str]:
    return [f.reason for f in hygiene.check_paths(root, paths)]


def test_clean_files_pass(tmp_path: Path) -> None:
    rel = _write(tmp_path, "src/ok.py", "print('hello')\n")
    assert _reasons(tmp_path, rel) == []


@pytest.mark.parametrize(
    "name", ["model.rvt", "family.RFA", "plan.dwg", "plan.dxf", "model.ifc", "drawing.pdf"]
)
def test_design_data_file_types_are_rejected(tmp_path: Path, name: str) -> None:
    rel = _write(tmp_path, f"data/{name}", b"x")
    (reason,) = _reasons(tmp_path, rel)
    assert "forbidden file type" in reason


def test_synthetic_fixture_dxf_is_allowed(tmp_path: Path) -> None:
    rel = _write(tmp_path, "tests/fixtures/synthetic/square_room.dxf", "0\nEOF\n")
    assert _reasons(tmp_path, rel) == []


def test_fixture_outside_synthetic_dir_is_rejected(tmp_path: Path) -> None:
    rel = _write(tmp_path, "tests/fixtures/real/customer.dxf", "0\nEOF\n")
    assert len(_reasons(tmp_path, rel)) == 1


@pytest.mark.parametrize(
    ("label", "secret"),
    [
        ("private key", "-----BEGIN " + "RSA PRIVATE KEY-----\nabc\n"),
        ("Anthropic API key", "KEY = 'sk-" + "ant-api03-" + "A" * 40 + "'"),
        ("GitHub token", "token: gh" + "p_" + "a" * 36),
        ("AWS access key id", "id=AK" + "IA" + "ABCDEFGHIJKLMNOP"),
    ],
)
def test_secrets_are_detected(tmp_path: Path, label: str, secret: str) -> None:
    rel = _write(tmp_path, "config/settings.txt", secret)
    reasons = _reasons(tmp_path, rel)
    assert any(label in r for r in reasons), reasons


def test_large_files_are_rejected(tmp_path: Path) -> None:
    rel = _write(tmp_path, "big.bin", b"\x00" * (hygiene.MAX_FILE_BYTES + 1))
    (reason,) = _reasons(tmp_path, rel)
    assert "limit" in reason


def test_binary_files_are_not_scanned_for_secrets(tmp_path: Path) -> None:
    rel = _write(tmp_path, "image.png", b"\x89PNG\x00" + b"sk-ant-" + b"A" * 40)
    assert _reasons(tmp_path, rel) == []


def test_missing_paths_are_ignored(tmp_path: Path) -> None:
    assert _reasons(tmp_path, "deleted.py") == []


def test_this_repository_is_clean() -> None:
    proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
