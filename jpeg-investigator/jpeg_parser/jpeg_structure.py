import json
from .segment_types import SEGMENT_TYPES

class JpegSegment():
    def __init__(self, segment_id: int, position: int) -> None:
        self.segment_id = segment_id
        self.info_dict = SEGMENT_TYPES.get(segment_id, None)
        self.position = position
        self.payload_length = 0

    def set_payload_length(self, payload_length: int) -> None:
        self.payload_length = payload_length

    def get_payload_length(self) -> int:
        return self.payload_length

class JpegStructure():
    def __init__(self) -> None:
        self.segments = []

    def add_segment(self, segment: JpegSegment) -> None:
        self.segments.append(segment.__dict__)

    def get_segments(self) -> list[JpegSegment]:
        return self.segments
