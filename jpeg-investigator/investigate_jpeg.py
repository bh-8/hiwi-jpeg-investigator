import argparse
import pathlib
import sys

from jpeg_parser.jpeg_parser import JpegParser
from segment_views import JpegInvestigationViewer
import investigation_info

INVESTIGATOR_VERSION = "2.1"

# JPEG references
# https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
# https://help.accusoft.com/ImageGear/v18.8/Linux/IGDLL-10-05.html

#TODO list:

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

#data handling
investigation_info = investigation_info.InvestigationInfo()
investigation_info.set_initial_investigation_info(
    jpeg_file,
    len(jpeg_parser.get_jpeg_bytes()),
    INVESTIGATOR_VERSION
)

#parse jpeg file
if not jpeg_parser.parse(investigation_info):
    print(f"ERROR: Mature error due jpeg parsing; make sure the provided data is in jpeg format!")
    sys.exit(11)

investigation_info.determine_coverage()

#calculations and data acquisition done
structure_views = JpegInvestigationViewer(jpeg_parser.get_jpeg_bytes(), investigation_info.__dict__)

if True: #report view
    print(structure_views.draw_report())

sys.exit(0)
