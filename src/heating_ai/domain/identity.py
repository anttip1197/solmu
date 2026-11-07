"""Stable internal identities and traceable source references.

ADDENDUM-0001 §1: every room must have a stable internal identity and a traceable
relationship to its source geometry, regardless of whether it originates from Revit,
DXF or a future source.

The internal ID is deliberately independent of room numbers and names, which are
neither guaranteed to be unique nor guaranteed to exist (ADDENDUM-0001 §4).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class RoomId:
    """Stable internal room identifier (UUID).

    Not derived from any source-system identifier, so it stays stable even if the
    source element is renumbered, renamed or re-imported from another format.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, uuid.UUID):
            raise TypeError(f"RoomId.value must be uuid.UUID, got {type(self.value).__name__}")

    @classmethod
    def new(cls) -> RoomId:
        """Generate a new random identifier."""
        return cls(uuid.uuid4())

    @classmethod
    def parse(cls, text: str) -> RoomId:
        """Parse a canonical UUID string. Raises ``ValueError`` on invalid input."""
        if not isinstance(text, str):
            raise TypeError(f"RoomId.parse expects str, got {type(text).__name__}")
        try:
            parsed = uuid.UUID(text)
        except ValueError as exc:
            raise ValueError(f"Invalid RoomId: {text!r}") from exc
        if str(parsed) != text.lower():
            # Reject non-canonical forms (braces, urn: prefix, missing hyphens) so that
            # serialized IDs round-trip byte-for-byte.
            raise ValueError(f"RoomId must be a canonical hyphenated UUID: {text!r}")
        return cls(parsed)

    def __str__(self) -> str:
        return str(self.value)


class SourceType(StrEnum):
    """Origin of a piece of building data."""

    REVIT = "revit"
    DXF = "dxf"


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Traceable reference from a domain object back to its source element.

    ``element_id`` is the identifier as given by the source system, kept as an opaque
    string (e.g. a Revit UniqueId or a DXF entity handle). Its format is not interpreted
    here; source-specific rules belong to adapters.

    ``document_ref`` optionally identifies the source document/file. It must not contain
    customer data beyond an identifier (AGENTS.md §7).
    """

    source_type: SourceType
    element_id: str
    document_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_type, SourceType):
            raise TypeError(f"source_type must be SourceType, got {type(self.source_type).__name__}")
        _require_non_blank("element_id", self.element_id)
        if self.document_ref is not None:
            _require_non_blank("document_ref", self.document_ref)


def _require_non_blank(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str, got {type(value).__name__}")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty or whitespace")
    if value != value.strip():
        raise ValueError(f"{field_name} must not have leading or trailing whitespace")
