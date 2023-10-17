import binascii
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

        # table header
        tt.header([
            "segment id",
            "segment label",
            "position",
            "length",
            "crc32",
            "segment description"
        ])

        coverage_gaps = self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"]
        for segment in self.investigation_info_dict["segments"]:
            # add segments
            tt.add_row([
                f"{'ff%0.2x' % segment['id']} ({segment['dict_entry']['abbr']})",
                segment["dict_entry"]["name"],
                segment["position"],
                segment["payload_length"],
                hex(0 if segment["crc32"] == None else segment["crc32"]),
                segment["dict_entry"]["info"]
            ])

            # determine whether unidentified data is following
            next_position = segment["position"] + segment["payload_length"] + 2
            if len(coverage_gaps) > 0:
                for fr, to in coverage_gaps:
                    if next_position == fr:
                        segment_data = self.jpeg_bytes[fr:to]
                        tt.add_row(["(!) unknown", "(unidentified data)", fr, to - fr, hex(binascii.crc32(segment_data)), f"{to - fr} unidentified bytes"])

        tt.set_deco(texttable.Texttable.HEADER)
        return tt.draw()

    def report_structure_characteristics(self) -> str:
        sb = ""

        # determine encoding
        encodings = self.investigation_info_dict["characteristics"]["encodings"]
        if len(encodings) > 0:
            if len(encodings) == 1:
                sb += f" - specified encoding is {encodings[0].lower()}\n"
            else:
                sb += f" - file features more than one encoding!\n"

        # count unidentified segments
        unidentified_segment_count = len(self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"])
        unidentified_bytes_total = 0
        for fr, to in self.investigation_info_dict["general_investigation_info"]["coverage"]["gaps"]:
            unidentified_bytes_total += to - fr
        if unidentified_segment_count > 0:
            sb += f" - encountered {'1 uncovered data segment' if unidentified_segment_count == 1 else str(unidentified_segment_count) + ' distinct uncovered data segments'} in the file ({unidentified_bytes_total} bytes, {round((1 - self.investigation_info_dict['general_investigation_info']['coverage']['percentage']) * 100, 5)}%).\n"

        # count quantization tables
        quantization_tables = self.investigation_info_dict["characteristics"]["quantization_tables"]
        if len(quantization_tables) > 0:
            sb += f" - quantization tables in {'1 segment' if len(quantization_tables) == 1 else str(len(quantization_tables)) + ' distinct segments'}\n"

        # count huffman tables
        huffman_tables = self.investigation_info_dict["characteristics"]["huffman_tables"]
        if len(huffman_tables) > 0:
            sb += f" - huffman tables in {'1 segment' if len(huffman_tables) == 1 else str(len(huffman_tables)) + ' distinct segments'}\n"

        # count icc profiles
        icc_profiles = self.investigation_info_dict["characteristics"]["icc_profiles"]
        if len(icc_profiles) > 0:
            sb += f" - icc profiles in {'1 segment' if len(icc_profiles) == 1 else str(len(icc_profiles)) + ' distinct segments'}\n"

        # count exif segments
        exif_data = self.investigation_info_dict["characteristics"]["exif_data"]
        if len(exif_data) > 0:
            sb += f" - exif data in {'1 segment' if len(exif_data) == 1 else str(len(exif_data)) + ' distinct segments'}\n"

        # count xmp profiles
        xmp_profiles = self.investigation_info_dict["characteristics"]["xmp_profiles"]
        if len(xmp_profiles) > 0:
            sb += f" - xmp profiles in {'1 segment' if len(xmp_profiles) == 1 else str(len(xmp_profiles)) + ' distinct segments'}\n"

        # count photoshop embeds
        photoshop_data = self.investigation_info_dict["characteristics"]["photoshop_data"]
        if len(photoshop_data) > 0:
            sb += f" - photoshop data in {'1 segment' if len(photoshop_data) == 1 else str(len(photoshop_data)) + ' distinct segments'}\n"

        # count parsing errors
        null_segments = self.investigation_info_dict["characteristics"]["null_segments"]
        if len(null_segments) > 0:
            sb += f" - null segments on {'1 position' if len(null_segments) == 1 else str(len(null_segments)) + ' distinct positions'}\n"

        return sb

    def report_stego_signatures(self) -> str:
        sb = ""
        for stego_tool, stego_signatures in self.investigation_info_dict["stego_attributes"].items():
            for attribute, triggered in stego_signatures.items():
                if triggered:
                    sb += f" - {stego_tool}: {attribute}\n"
        return " - none\n" if sb == "" else sb

    def report_critical(self) -> str:
        sb = ""
        for error, value in self.investigation_info_dict["integrity_errors"].items():
            if not value == None:
                sb += f" - {error}: {value}\n"
        return " - none\n" if sb == "" else sb

    def as_json(self, indent: int = 0) -> str:
        return json.dumps(self.investigation_info_dict, indent=None if indent == 0 else indent)
