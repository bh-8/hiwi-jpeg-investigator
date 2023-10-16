import argparse
import pathlib
import sys

from jpeg_parser.jpeg_parser import JpegParser
from segment_views import JpegInvestigationViewer
from segment_coverage import determine_gaps

INVESTIGATOR_VERSION = "1.0"

# JPEG references
# https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
# https://help.accusoft.com/ImageGear/v18.8/Linux/IGDLL-10-05.html

#TODO list:
# - triggered stego attributes initiate a warning with attrib count

# - thumbnail extraction using exiftool
#exifexec = [
#    "exiftool",
#    "-a",
#    "-b",
#    "-W",
#    f"{str(outfilePath.parent / outfilePath.stem)}.%t%c.%s",
#    "-preview:all",
#    str(infile)
#]
#exifResultStr = subprocess.check_output(exifexec).strip(b"\x20\n").decode(errors = "ignore")#, stderr = subprocess.STDOUT)
#exifThumbnailNum = exifResultStr.split(" ")[0]
#print(exifResultStr)

# - add SOF characteristic as encoding

# - switch output to json format
# - redirect output to file
# - how could a message straigh before EOI marker be detected?

# - payload extraction by segment

# - verify outguess signature correctness

# - implement camouflage detection, maybe other attributes..
# - photoshop data: identify exact type; see https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/

parser = argparse.ArgumentParser(
    prog="./investigate-jpeg",
    description=f"JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection.",
    epilog=f"JPEG investigator v{INVESTIGATOR_VERSION}"
)

parser.add_argument("jpeg_file")
args = parser.parse_args()

jpeg_file = pathlib.Path(args.jpeg_file).resolve()
jpeg_parser = JpegParser()

#read jpeg file
if not jpeg_parser.read_jpeg_file(jpeg_file):
    print(f"ERROR: Could not access jpeg data: '{jpeg_file}'!")
    sys.exit(10)

#parse jpeg file
if not jpeg_parser.parse():
    print(f"ERROR: Mature error due jpeg parsing; make sure the provided data is in jpeg format!")
    sys.exit(11)

#get data
parsed_data = jpeg_parser.complete_dict()

if not "segments" in parsed_data:
    print(f"ERROR: Segment list is empty!")
    sys.exit(12)

#determine coverage
coverage_gaps = determine_gaps(parsed_data)

#initialize views
structure_views = JpegInvestigationViewer(jpeg_parser.get_jpeg_bytes(), parsed_data, coverage_gaps)

if True: #report view
    print(f"[JPEG INVESTIGATOR REPORT START]")
    print(f"\ngeneral investigation info:")
    print(f" - investigated file: '{jpeg_file}'")
    print(f" - file size: {parsed_data['parsing_stats']['data_length']} bytes")
    print(f" - identified data: {round(structure_views.calculate_coverage_percentage() * 100, 5)}%")
    print(f" - investigator version: {INVESTIGATOR_VERSION}")
    print(f"\njpeg segment table:")
    [print(f" {l}") for l in structure_views.report_segment_table().splitlines()]

    print(f"\nstructure characteristics:")
    print(structure_views.report_structure_characteristics())
    print(f"errors/warnings:")
    print(structure_views.report_critical())
    print(f"stego attributes:")
    print(structure_views.report_stego_signatures())
    print(f"[JPEG INVESTIGATOR REPORT END]")

sys.exit(0)
