import dataclasses
import uuid

import pytest

from heating_ai.domain import RoomId, SourceReference, SourceType


class TestRoomId:
    def test_new_generates_distinct_ids(self) -> None:
        assert RoomId.new() != RoomId.new()

    def test_parse_round_trips_canonical_string(self) -> None:
        text = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
        room_id = RoomId.parse(text)
        assert str(room_id) == text
        assert RoomId.parse(str(room_id)) == room_id

    def test_parse_accepts_uppercase(self) -> None:
        text = "3F2504E0-4F89-41D3-9A0C-0305E82C3301"
        assert str(RoomId.parse(text)) == text.lower()

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "not-a-uuid",
            "3f2504e04f8941d39a0c0305e82c3301",  # no hyphens
            "{3f2504e0-4f89-41d3-9a0c-0305e82c3301}",  # braces
            "urn:uuid:3f2504e0-4f89-41d3-9a0c-0305e82c3301",
            " 3f2504e0-4f89-41d3-9a0c-0305e82c3301",
        ],
    )
    def test_parse_rejects_invalid_or_non_canonical(self, text: str) -> None:
        with pytest.raises(ValueError):
            RoomId.parse(text)

    def test_parse_rejects_non_string(self) -> None:
        with pytest.raises(TypeError):
            RoomId.parse(123)  # type: ignore[arg-type]

    def test_constructor_rejects_non_uuid(self) -> None:
        with pytest.raises(TypeError):
            RoomId("3f2504e0-4f89-41d3-9a0c-0305e82c3301")  # type: ignore[arg-type]

    def test_is_immutable_and_hashable(self) -> None:
        room_id = RoomId.new()
        with pytest.raises(dataclasses.FrozenInstanceError):
            room_id.value = uuid.uuid4()  # type: ignore[misc]
        assert {room_id, RoomId(room_id.value)} == {room_id}


class TestSourceReference:
    def test_valid_revit_reference(self) -> None:
        ref = SourceReference(SourceType.REVIT, "a1b2c3-0001e240", document_ref="model-A")
        assert ref.source_type is SourceType.REVIT
        assert ref.element_id == "a1b2c3-0001e240"
        assert ref.document_ref == "model-A"

    def test_document_ref_is_optional(self) -> None:
        assert SourceReference(SourceType.DXF, "1F4").document_ref is None

    def test_same_element_id_from_different_sources_is_distinct(self) -> None:
        assert SourceReference(SourceType.REVIT, "42") != SourceReference(SourceType.DXF, "42")

    @pytest.mark.parametrize("element_id", ["", "   ", " 42", "42 "])
    def test_rejects_blank_or_padded_element_id(self, element_id: str) -> None:
        with pytest.raises(ValueError):
            SourceReference(SourceType.REVIT, element_id)

    def test_rejects_missing_element_id(self) -> None:
        with pytest.raises(TypeError):
            SourceReference(SourceType.REVIT, None)  # type: ignore[arg-type]

    def test_rejects_blank_document_ref(self) -> None:
        with pytest.raises(ValueError):
            SourceReference(SourceType.REVIT, "42", document_ref="")

    def test_rejects_plain_string_source_type(self) -> None:
        with pytest.raises(TypeError):
            SourceReference("revit", "42")  # type: ignore[arg-type]

    def test_source_type_values_are_stable_strings(self) -> None:
        # These values are expected to appear in serialized contracts later (FND-005).
        assert {t.value for t in SourceType} == {"revit", "dxf"}
