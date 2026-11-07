"""Repository hygiene check (FND-004, NFR-003, AGENTS.md §7).

Fails if version control contains:
- customer/design data file types (Revit, CAD, IFC, Navisworks, PDF drawings),
- unexpectedly large files,
- recognisable secrets (private keys, common API token formats).

Synthetic, provenance-documented fixtures may be stored under ``tests/fixtures/synthetic/``.
Standard library only. Usage: ``python tools/check_repo_hygiene.py`` (checks ``git ls-files``).
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

FORBIDDEN_SUFFIXES = frozenset(
    {".rvt", ".rfa", ".rte", ".rft", ".dwg", ".dxf", ".ifc", ".nwc", ".nwd", ".pdf"}
)
SYNTHETIC_FIXTURE_DIR = PurePosixPath("tests/fixtures/synthetic")
MAX_FILE_BYTES = 5 * 1024 * 1024

# Patterns are assembled from parts so that this file does not match itself.
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key", re.compile("-----BEGIN " + r"(?:[A-Z]+ )?PRIVATE KEY-----")),
    ("Anthropic API key", re.compile(r"\b" + "sk-" + r"ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI-style API key", re.compile(r"\b" + "sk-" + r"(?:proj-)?[A-Za-z0-9]{32,}")),
    ("GitHub token", re.compile(r"\b(?:" + "gh" + r"[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("AWS access key id", re.compile(r"\b" + "AK" + r"IA[0-9A-Z]{16}\b")),
)


@dataclass(frozen=True)
class Finding:
    path: str
    reason: str

    def __str__(self) -> str:
        return f"{self.path}: {self.reason}"


def _is_synthetic_fixture(path: PurePosixPath) -> bool:
    return path.is_relative_to(SYNTHETIC_FIXTURE_DIR)


def check_paths(root: Path, paths: Iterable[str]) -> list[Finding]:
    """Check the given repository-relative paths below ``root``."""
    findings: list[Finding] = []
    for raw in paths:
        rel = PurePosixPath(raw)
        if rel.suffix.lower() in FORBIDDEN_SUFFIXES and not _is_synthetic_fixture(rel):
            findings.append(Finding(raw, f"forbidden file type {rel.suffix.lower()} (design/customer data)"))
            continue
        file = root / raw
        if not file.is_file():
            continue  # deleted in working tree, submodule, etc.
        size = file.stat().st_size
        if size > MAX_FILE_BYTES:
            findings.append(Finding(raw, f"file is {size} bytes, limit {MAX_FILE_BYTES}"))
            continue
        data = file.read_bytes()
        if b"\x00" in data[:8192]:
            continue  # binary
        text = data.decode("utf-8", errors="replace")
        for name, pattern in _SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(Finding(raw, f"looks like a {name}"))
    return findings


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout.decode(
        "utf-8"
    )
    return [p for p in out.split("\0") if p]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    findings = check_paths(root, tracked_files(root))
    for f in findings:
        print(f"HYGIENE: {f}", file=sys.stderr)
    if findings:
        print(f"{len(findings)} problem(s) found. See AGENTS.md §7.", file=sys.stderr)
        return 1
    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
