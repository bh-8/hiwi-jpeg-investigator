import pathlib

class InvestigationInfo():
    def __init__(self) -> None:
        # general info
        self.general_investigation_info = {
            "investigated_file": None,
            "file_size": None,
            "coverage": {
                "unidentified_data": None,
                "unknown_segments": None,
                "percentage": None
            },
            "investigator_version": None
        }

        # segment list
        self.segments = None

        # characteristics
        self.characteristics = {
            "encodings": [],

            "quantization_tables": [],
            "huffman_tables": [],
            "icc_profiles": [],
            "exif_data": [],
            "xmp_profiles": [],
            "photoshop_data": [],

            "null_segments": []
        }

        # errors
        self.integrity_errors = {
            "eoi_marker_not_found": None,
            "magic_number_misplaced": None,
            "magic_number_not_found": f"magic number could not be found: not a valid jpeg file",
            "encoding_not_defined": f"jpeg file does not contain any start of frame segment",
            "multiple_encodings_defined": None,
            "null_segments": None,
            "unknown_segments_found": None,
            "stego_attribute_triggered": None
        }

        # attributes
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

    def set_initial_investigation_info(self, investigated_file: pathlib.Path, file_size: int, investigator_version: str) -> None:
        self.general_investigation_info["investigated_file"] = str(investigated_file)
        self.general_investigation_info["file_size"] = file_size
        self.general_investigation_info["investigator_version"] = investigator_version

    def get_general_investigation_info(self) -> None:
        return self.general_investigation_info

    def set_segment_info(self, segments: dict) -> None:
        self.segments = segments

    def add_characteristic(self, characteristic: str, value) -> None:
        self.characteristics[characteristic].append(value)

    def set_integrity_error(self, error: str, value: str):
        self.integrity_errors[error] = value

    def set_stego_attribute(self, stego_tool: str, attribute: str, value: bool) -> None:
        if value:
            self.integrity_errors["stego_attribute_triggered"] = f"found potential steganography-related signature(s)"
        self.stego_attributes[stego_tool][attribute] = value

    def determine_coverage(self) -> None:
        unidentified_data = []
        unknown_segments = []

        compare_position = 0
        for segment in self.segments:
            if segment["position"] != compare_position:
                unidentified_data.append((compare_position, segment["position"]))
            if segment["dict_entry"]["abbr"] == "unknown":
                unknown_segments.append((segment["position"] + 2, segment["position"] + 2 + segment["payload_length"]))
            compare_position = segment["position"] + segment["payload_length"] + 2

        #check if last segment is not eof yet
        if self.general_investigation_info["file_size"] != compare_position:
            unidentified_data.append((compare_position, self.general_investigation_info["file_size"]))

        if not len(unidentified_data) == 0:
            self.set_integrity_error("unidentified_data_found", "file contains unknown data")

        self.general_investigation_info["coverage"]["unidentified_data"] = unidentified_data
        self.general_investigation_info["coverage"]["unknown_segments"] = unknown_segments

        # sum unidentified bytes
        uncovered_bytes = 0
        for fr, to in unidentified_data:
            uncovered_bytes += to - fr
        for fr, to in unknown_segments:
            uncovered_bytes += to - fr

        # set coverage percentage
        self.general_investigation_info["coverage"]["percentage"] = (self.general_investigation_info["file_size"] - uncovered_bytes) / self.general_investigation_info["file_size"]

    def filter_segments_view(self, search_segments: str) -> list:
        unidentified_data = self.general_investigation_info["coverage"]["unidentified_data"]

        # star operation (all segments)
        search_segment_list = None
        if search_segments == "*":
            search_segment_list = [i["dict_entry"]["abbr"].lower() for i in self.segments]
            search_segment_list.append("unknown")
        else:
            search_segment_list = search_segments.split(",")

        # collect filtered segments
        filtered_segments = []
        for search_segment in search_segment_list:
            segment_counter = 0
            for segment in self.segments:
                hex_id = f"{'ff%0.2x' % segment['id']}"
                abbr_id = segment['dict_entry']['abbr'].lower()
                pos = segment['position'] + 2
                length = segment['payload_length']

                # check default segments
                if (search_segment in hex_id) or (search_segment in abbr_id):
                    filtered_segments.append({
                        "id": f"{abbr_id}-{hex_id}-{segment_counter}",
                        "fr": pos,
                        "to": pos + length
                    })
                    segment_counter += 1

                # unidentified data
                if len(unidentified_data) > 0 and search_segment in "unknown":
                    next_position = segment["position"] + segment["payload_length"] + 2
                    for fr, to in unidentified_data:
                        if next_position == fr:
                            filtered_segments.append({
                                "id": f"unknown-{segment_counter}",
                                "fr": fr,
                                "to": to
                            })
                            segment_counter += 1
        return filtered_segments
