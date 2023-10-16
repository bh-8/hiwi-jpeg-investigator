import json
import texttable

class JpegInvestigationViewer():
    def __init__(self, jpeg_bytes: bytes, investigation_info_dict: dict) -> None:
        self.jpeg_bytes = jpeg_bytes
        self.investigation_info_dict = investigation_info_dict

    def draw_report(self) -> str:
        sb = "[JPEG INVESTIGATOR REPORT START]\n"

        sb += "\ngeneral investigation info:\n"
        sb += f" - investigated file: '{self.investigation_info_dict['general_investigation_info']['investigated_file']}'\n"
        sb += f" - file size: {self.investigation_info_dict['general_investigation_info']['file_size']} bytes\n"
        sb += f" - identified data: {round(self.investigation_info_dict['general_investigation_info']['coverage']['percentage'] * 100, 5)}%\n"
        sb += f" - investigator version: {self.investigation_info_dict['general_investigation_info']['investigator_version']}\n"
    
        sb += "\njpeg segment table:\n"
        for l in self.report_segment_table().splitlines():
            sb += f" {l}\n"

        sb += "\nstructure characteristics:\n"
        sb += self.report_structure_characteristics()

        sb += "\nerrors/warnings:\n"
        sb += self.report_critical()

        sb += "\nstego attributes:\n"
        sb += self.report_stego_signatures()

        return sb + "\n[JPEG INVESTIGATOR REPORT END]"

    def report_segment_table(self) -> str:
        tt = texttable.Texttable(120)
        tt.header([
            "segment id",
            "name",
            "position",
            "data length",
            "description"
        ])

        coverage_gaps = self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"]
        for segment in self.investigation_info_dict["segments"]:
            
            tt.add_row([
                f"{'ff%0.2x' % segment['id']} ({segment['dict_entry']['abbr']})",
                segment["dict_entry"]["name"],
                segment["position"],
                segment["payload_length"],
                segment["dict_entry"]["info"]
            ])

            next_position = segment["position"] + segment["payload_length"] + 2
            if len(coverage_gaps) > 0:
                for fr, to in coverage_gaps:
                    if next_position == fr:
                        tt.add_row(["(!)", "(unidentified data)", fr, to - fr, f"{to - fr} unidentified bytes"])

        tt.set_deco(texttable.Texttable.HEADER)
        return tt.draw()

    def report_structure_characteristics(self) -> str:
        sb = ""

        unidentified_segment_count = len(self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"])
        unidentified_bytes_total = 0
        for fr, to in self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"]:
            unidentified_bytes_total += to - fr
        if unidentified_segment_count > 0:
            sb += f" - Encountered {'1 uncovered data segment' if unidentified_segment_count == 1 else str(unidentified_segment_count) + ' distinct uncovered data segments'} in the file ({unidentified_bytes_total} bytes, {round((1 - self.investigation_info_dict['general_investigation_info']['coverage']['percentage']) * 100, 5)}%).\n"

        quantization_tables = self.investigation_info_dict["characteristics"]["quantization_tables"]
        if len(quantization_tables) > 0:
            sb += f" - Quantization tables in {'1 segment' if len(quantization_tables) == 1 else str(len(quantization_tables)) + ' distinct segments'}\n"

        huffman_tables = self.investigation_info_dict["characteristics"]["huffman_tables"]
        if len(huffman_tables) > 0:
            sb += f" - Huffman tables in {'1 segment' if len(huffman_tables) == 1 else str(len(huffman_tables)) + ' distinct segments'}\n"

        icc_profiles = self.investigation_info_dict["characteristics"]["icc_profiles"]
        if len(icc_profiles) > 0:
            sb += f" - ICC profiles in {'1 segment' if len(icc_profiles) == 1 else str(len(icc_profiles)) + ' distinct segments'}\n"

        exif_data = self.investigation_info_dict["characteristics"]["exif_data"]
        if len(exif_data) > 0:
            sb += f" - Exif data in {'1 segment' if len(exif_data) == 1 else str(len(exif_data)) + ' distinct segments'}\n"

        xmp_profiles = self.investigation_info_dict["characteristics"]["xmp_profiles"]
        if len(xmp_profiles) > 0:
            sb += f" - XMP profiles in {'1 segment' if len(xmp_profiles) == 1 else str(len(xmp_profiles)) + ' distinct segments'}\n"

        photoshop_data = self.investigation_info_dict["characteristics"]["photoshop_data"]
        if len(photoshop_data) > 0:
            sb += f" - Photoshop data in {'1 segment' if len(photoshop_data) == 1 else str(len(photoshop_data)) + ' distinct segments'}\n"

        null_segments = self.investigation_info_dict["characteristics"]["null_segments"]
        if len(null_segments) > 0:
            sb += f" - Null segments on {'1 position' if len(null_segments) == 1 else str(len(null_segments)) + ' distinct positions'}!\n"

        return sb

    def report_stego_signatures(self) -> str:
        sb = ""
        for stego_tool, stego_signatures in self.investigation_info_dict["stego_attributes"].items():
            for attribute, triggered in stego_signatures.items():
                if triggered:
                    sb += f" - {stego_tool}: {attribute}\n"
        return " - None\n" if sb == "" else sb

    def report_critical(self) -> str:
        sb = ""
        for error, value in self.investigation_info_dict["integrity_errors"].items():
            if not value == None:
                sb += f" - {error}: {value}\n"
        return " - None\n" if sb == "" else sb

    def as_json(self, indent: int = 0) -> str:
        return json.dumps(self.investigation_info_dict, indent=None if indent == 0 else indent)
