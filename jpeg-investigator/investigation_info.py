from pathlib import Path

class InvestigationInfo():
    def __init__(self) -> None:
        self.general_investigation_info = {
            "investigated_file": None,
            "file_size": None,
            "coverage": {
                "gaps": None,
                "percentage": None
            },
            "investigator_version": None
        }
        self.segments = None
        self.characteristics = {
            "quantization_tables": [],
            "huffman_tables": [],
            "icc_profiles": [],
            "exif_data": [],
            "xmp_profiles": [],
            "photoshop_data": [],

            "null_segments": []
        }
        self.integrity_errors = {
            "eoi_marker_not_found": None,
            "magic_number_misplaced": None,
            "magic_number_not_found": f"Magic Number could not be found: Not a valid JPEG file!",
            "null_segments": None,
            "stego_attribute_triggered": None
        }
        self.stego_attributes = {
            "f5": {
                "suspicious_quantization_table": False
            },
            "jsteg": {
                "jfif_marker_not_found": True,
                "eoi_marker_not_found": False
            },
            "outguess": {
                "suspicious_quantization_table": False
            }
        }

    def set_initial_investigation_info(self, investigated_file: Path, file_size: int, investigator_version: str) -> None:
        self.general_investigation_info["investigated_file"] = str(investigated_file)
        self.general_investigation_info["file_size"] = file_size
        self.general_investigation_info["investigator_version"] = investigator_version

    def get_general_investigation_info(self) -> None:
        return self.general_investigation_info

    def set_segment_info(self, segments: dict) -> None:
        self.segments = segments

    def add_characteristic(self, characteristic: str, ff_position: int) -> None:
        self.characteristics[characteristic].append(ff_position)

    def set_integrity_error(self, error: str, value: str):
        self.integrity_errors[error] = value

    def set_stego_attribute(self, stego_tool: str, attribute: str, value: bool) -> None:
        if value:
            self.integrity_errors["stego_attribute_triggered"] = f"Found potential steganography-related signature(s)!"
        self.stego_attributes[stego_tool][attribute] = value

    def determine_coverage(self) -> None:
        uncovered_gaps = []

        compare_position = 0
        for segment in self.segments:
            if segment["position"] != compare_position:
                uncovered_gaps.append((compare_position, segment["position"]))

            compare_position = segment["position"] + segment["payload_length"] + 2

        #check if last segment is not eof yet
        if self.general_investigation_info["file_size"] != compare_position:
            uncovered_gaps.append((compare_position, self.general_investigation_info["file_size"]))

        if not len(uncovered_gaps) == 0:
            self.set_integrity_error("unidentified_data_found", f"File contains unknown data!")

        self.general_investigation_info["coverage"]["gaps"] = uncovered_gaps

        uncovered_bytes = 0
        for fr, to in uncovered_gaps:
            uncovered_bytes += to - fr

        self.general_investigation_info["coverage"]["percentage"] = (self.general_investigation_info["file_size"] - uncovered_bytes) / self.general_investigation_info["file_size"]

    def filter_segments_view(self, search_segments: str) -> list:
        coverage_gaps = self.general_investigation_info["coverage"]["gaps"]

        search_segment_list = None
        if search_segments == "*":
            search_segment_list = [i["dict_entry"]["abbr"].lower() for i in self.segments]
            search_segment_list.append("unknown")
        else:
            search_segment_list = search_segments.split(",")

        filtered_segments = []

        for search_segment in search_segment_list:
            segment_counter = 0
            for segment in self.segments:
                hex_id = f"{'ff%0.2x' % segment['id']}"
                abbr_id = segment['dict_entry']['abbr'].lower()
                pos = segment['position'] + 2
                length = segment['payload_length']

                if (search_segment in hex_id) or (search_segment in abbr_id):
                    filtered_segments.append({
                        "id": f"{abbr_id}-{hex_id}-{segment_counter}",
                        "fr": pos,
                        "to": pos + length
                    })
                    segment_counter += 1

                if len(coverage_gaps) > 0 and search_segment in "unknown":
                    next_position = segment["position"] + segment["payload_length"] + 2
                    for fr, to in coverage_gaps:
                        if next_position == fr:
                            filtered_segments.append({
                                "id": f"unknown-{segment_counter}",
                                "fr": fr,
                                "to": to
                            })
                            segment_counter += 1
        return filtered_segments
