"""Pure domain model.

Rules (see AGENTS.md §4):
- Standard library only. No Revit API, pyRevit, ``clr``, network, file or AI dependencies.
- Domain objects are immutable and validate their inputs on construction.
"""

from heating_ai.domain.identity import RoomId, SourceReference, SourceType

__all__ = ["RoomId", "SourceReference", "SourceType"]
