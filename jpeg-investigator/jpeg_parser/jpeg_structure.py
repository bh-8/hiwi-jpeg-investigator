import json
from .segment_types import SEGMENT_TYPES

class JpegSegment():
    def __init__(self, id: int, position: int) -> None:
        self.id = id
        self.dict_entry = SEGMENT_TYPES.get(id, None)
        self.position = position
        self.payload_length = 0
        self.header = None
        self.payload = None

    def set_payload_length(self, payload_length: int) -> None:
        self.payload_length = payload_length

    def get_payload_length(self) -> int:
        return self.payload_length

    def set_segment_data(self, header: bytes, payload: bytes) -> None:
        self.header = str(header)
        self.payload = str(payload)

class JpegStructure():
    def __init__(self) -> None:
        self.segments = []

    def add_segment(self, segment: JpegSegment) -> None:
        self.segments.append(segment.__dict__)

    def get_segments(self) -> list[JpegSegment]:
        return self.segments
