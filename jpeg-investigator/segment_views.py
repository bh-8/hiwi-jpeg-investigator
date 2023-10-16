import json
import texttable

class JpegInvestigationViewer():
    def __init__(self, jpeg_bytes: bytes, parsing_data_dict: dict, coverage_gaps: list) -> None:
        self.jpeg_bytes = jpeg_bytes
        self.parsing_data_dict = parsing_data_dict
        self.coverage_gaps = coverage_gaps
        
        self.uncovered_bytes = 0
        for fr, to in self.coverage_gaps:
            self.uncovered_bytes += to - fr

    def calculate_coverage_percentage(self) -> float:
        return (self.parsing_data_dict["parsing_stats"]["data_length"] - self.uncovered_bytes) / self.parsing_data_dict["parsing_stats"]["data_length"]

    def report_segment_table(self) -> str:
        tt = texttable.Texttable(120)
        tt.header([
            "segment id",
            "name",
            "position",
            "data length",
            "description"
        ])

        for segment in self.parsing_data_dict["segments"]:
            tt.add_row([
                f"{'ff%0.2x' % segment['id']} ({segment['dict_entry']['abbr']})",
                segment["dict_entry"]["name"],
                segment["position"],
                segment["payload_length"],
                segment["dict_entry"]["info"]
            ])

        tt.set_deco(texttable.Texttable.HEADER)
        return tt.draw()

    def report_stego_signatures(self) -> str:
        sb = ""
        for stego_tool, stego_signatures in self.parsing_data_dict["stego_signatures"].items():
            for attribute, triggered in stego_signatures.items():
                if triggered:
                    sb += f" - {stego_tool}: {attribute}\n"
        return " - None\n" if sb == "" else sb

    def report_structure_characteristics(self) -> str:
        sb = ""

        if len(self.coverage_gaps) > 0:
            sb += f" - Encountered {'1 uncovered data segment' if len(self.coverage_gaps) == 1 else str(len(self.coverage_gaps)) + ' distinct uncovered data segments'} in the file ({self.uncovered_bytes} bytes, {round((1 - self.calculate_coverage_percentage()) * 100, 5)}%).\n"

        quantization_tables = self.parsing_data_dict["parsing_stats"]["quantization_tables"]
        if len(quantization_tables) > 0:
            sb += f" - Quantization tables in {'1 segment' if len(quantization_tables) == 1 else str(len(quantization_tables)) + ' distinct segments'}\n"

        huffman_tables = self.parsing_data_dict["parsing_stats"]["huffman_tables"]
        if len(huffman_tables) > 0:
            sb += f" - Huffman tables in {'1 segment' if len(huffman_tables) == 1 else str(len(huffman_tables)) + ' distinct segments'}\n"

        icc_profiles = self.parsing_data_dict["parsing_stats"]["icc_profiles"]
        if len(icc_profiles) > 0:
            sb += f" - ICC profiles in {'1 segment' if len(icc_profiles) == 1 else str(len(icc_profiles)) + ' distinct segments'}\n"

        xmp_profiles = self.parsing_data_dict["parsing_stats"]["xmp_profiles"]
        if len(xmp_profiles) > 0:
            sb += f" - XMP profiles in {'1 segment' if len(xmp_profiles) == 1 else str(len(xmp_profiles)) + ' distinct segments'}\n"

        exif_data = self.parsing_data_dict["parsing_stats"]["exif_data"]
        if len(exif_data) > 0:
            sb += f" - Exif data in {'1 segment' if len(exif_data) == 1 else str(len(exif_data)) + ' distinct segments'}\n"

        photoshop_data = self.parsing_data_dict["parsing_stats"]["photoshop_data"]
        if len(photoshop_data) > 0:
            sb += f" - Photoshop data in {'1 segment' if len(photoshop_data) == 1 else str(len(photoshop_data)) + ' distinct segments'}\n"

        return sb

    def report_critical(self) -> str:
        sb = ""
        for error, value in self.parsing_data_dict["integrity_errors"].items():
            if not value == None:
                sb += f" - {error}: {value}\n"
        null_segments = self.parsing_data_dict["parsing_stats"]["null_segments"]
        if len(null_segments) > 0:
            sb += f" - null segments on {'1 position' if len(null_segments) == 1 else str(len(null_segments)) + ' distinct positions'}!\n"
        return " - None\n" if sb == "" else sb

    def as_json(self, indent: int = 0) -> str:
        return json.dumps(self.parsing_data_dict, indent=None if indent == 0 else indent)
