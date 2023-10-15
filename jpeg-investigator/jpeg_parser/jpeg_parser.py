import pathlib
from .jpeg_structure import JpegStructure, JpegSegment
from .segment_utils import *

class JpegParser():
    def __init__(self) -> None:
        self.jpeg_bytes = None

        self.jpeg_structure = None
        self.parsing_stats = {
            "exif_data": [],
            "icc_profiles": [],
            "null_segments": [],
            "photoshop_data": [],
            "xmp_profiles": []
        }
        self.stego_signatures = {
            "jsteg": {
                "eoi_marker_broken": False
            }
        }
        self.integrity_errors = {
            "eoi_segment_not_found": None
        }

    def read_jpeg_bytes(self, jpeg_bytes: bytes) -> bool:
        self.jpeg_bytes = jpeg_bytes
        return jpeg_bytes != None and len(self.jpeg_bytes) != 0

    def read_jpeg_file(self, jpeg_file: pathlib.Path) -> bool:
        if not jpeg_file.exists():
            return False
        
        with open(jpeg_file, "rb") as file_handle:
            return self.read_jpeg_bytes(file_handle.read())

    def parse(self) -> bool:
        if self.jpeg_bytes == None:
            return False

        parsing_done = False
        parsing_search_offset = 0
        self.jpeg_structure = JpegStructure()

        while not parsing_done:
            #search for next 0xff appearance
            print(f"[DEBUG] Searching from position {parsing_search_offset}...")
            ff_position = self.jpeg_bytes.find(b"\xff", parsing_search_offset)
            print(f"[DEBUG] Hit position {ff_position}...")

            #in case nothing was found, done
            if ff_position == -1:
                parsing_done = True
                continue

            segment_id_position = ff_position + 1

            #check if segment_id_position is in bounds
            if segment_id_position >= len(self.jpeg_bytes):
                parsing_done = True
                continue

            segment_id = self.jpeg_bytes[segment_id_position]
            new_segment = JpegSegment(segment_id, ff_position)

            if segment_id == 0 or segment_id == 255:
                # \xff\x00 and \xff\xff
                self.parsing_stats["null_segments"].append(ff_position)
                
                parsing_search_offset = ff_position + 2
                continue
            if segment_id == 216:
                # \xff\xd8 - Magic Number
                self.jpeg_structure.add_segment(new_segment)
                
                parsing_search_offset = ff_position + 2
                continue
            if segment_id == 217:
                # \xff\xd9 - End of Image
                self.jpeg_structure.add_segment(new_segment)
                
                parsing_search_offset = ff_position + 2
                continue

            payload_position = ff_position + 2
            new_segment.set_payload_length(calculate_default_payload_length(self.jpeg_bytes, payload_position))

            if segment_id == 218:
                # \xff\xda - Start of Scan
                eoi_position = self.jpeg_bytes.find(b"\xff\xd9", ff_position + 2)
                if eoi_position == -1:
                    self.stego_signatures["jsteg"]["eoi_marker_broken"] = True
                    self.integrity_errors["eoi_segment_not_found"] = f"Could not find EOI segment after SOS marker!"
                else:
                    new_segment.set_payload_length(eoi_position - payload_position)
            elif segment_id == 225:
                # \xff\xe1 - Application 1
                if check_exif_signature(self.jpeg_bytes, payload_position):
                    self.parsing_stats["exif_data"].append(ff_position)
                if check_xmp_profile_signature(self.jpeg_bytes, payload_position):
                    XMP_END = b"<?xpacket end=\"w\"?>"
                    xmp_end_position = self.jpeg_bytes.find(XMP_END, payload_position)
                    if xmp_end_position != -1:
                        new_segment.set_payload_length(xmp_end_position + len(XMP_END) - payload_position)
                        self.parsing_stats["xmp_profiles"].append(ff_position)
            elif segment_id == 226:
                # \xff\xe2 - Application 2
                if check_icc_profile_signature(self.jpeg_bytes, payload_position):
                    self.parsing_stats["icc_profiles"].append(ff_position)
                    icc_profile_length_info = self.jpeg_bytes[payload_position + 14:payload_position + 16]
                    if icc_profile_length_info[0] < icc_profile_length_info[1]:
                        new_segment.set_payload_length(65535)
            elif segment_id == 237:
                # \xff\xed - Application 13
                if check_photoshop_signature(self.jpeg_bytes, payload_position):
                    self.parsing_stats["photoshop_data"].append(ff_position)
                    ps_signature_position = payload_position + 16
                    ps_signature = self.jpeg_bytes[ps_signature_position:ps_signature_position + 4].decode(errors = "ignore")
                    #TODO: match signatures...

            self.jpeg_structure.add_segment(new_segment)
            parsing_search_offset = ff_position + 2 + new_segment.get_payload_length()

        return True

    def complete_dict(self) -> dict:
        return {
            "segments": self.jpeg_structure.get_segments(),
            "parsing_stats": self.parsing_stats,
            "stego_signatures": self.stego_signatures,
            "integrity_errors": self.integrity_errors
        }

