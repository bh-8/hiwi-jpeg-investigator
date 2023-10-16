import argparse
import pathlib
import json
import sys

from jpeg_parser.jpeg_parser import JpegParser
from segment_views import JpegInvestigationViewer
from investigation_info import InvestigationInfo

INVESTIGATOR_VERSION = "2.1"

# JPEG references
# https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
# https://help.accusoft.com/ImageGear/v18.8/Linux/IGDLL-10-05.html
# ps data id: https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/

#TODO list:
# 1 add SOF characteristic as encoding
# 2 texttable alignment header row
# 3 refactoring, documentation
# 4 extract thumbnails
# 5 signature parameter accepts again list of segments
#   - calculate hash sum of those
# 6 verify outguess signature correctness

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

arg_parser = argparse.ArgumentParser(
    prog="./investigate-jpeg",
    description=f"JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection.",
    epilog=f"JPEG investigator v{INVESTIGATOR_VERSION}"
)

arg_parser.add_argument("jpeg_file", nargs="+", help="one or more JPEG files to investigate")
arg_parser.add_argument("-jf", "--json_file", help="export full investigation data as json")
arg_parser.add_argument("-ed", "--ext_dir", help="set path to store extracted segments")
arg_parser.add_argument("-es", "--ext_segs", help="specify segments to extract, e.g. app0,dqt")
arg_parser.add_argument("-f", "--force", action="store_true", help="force file overwrite when exporting")
arg_parser.add_argument("-s", "--silent", action="store_true", help="no output on stdout")

args = arg_parser.parse_args()

json_file = None if args.json_file == None else pathlib.Path(args.json_file).resolve()
ext_dir = None if args.ext_dir == None else pathlib.Path(args.ext_dir).resolve()
ext_segs = None if args.ext_segs == None else args.ext_segs.lower()
force_overwrite = args.force
has_to_be_silent = args.silent

if (ext_segs != None and ext_dir == None):
    print(f"ERROR: Parameter '--ext_segs' requires '--ext_dir'!")
    sys.exit(13)

complete_dict = {}

for _jpeg_file in args.jpeg_file:
    jpeg_file = pathlib.Path(_jpeg_file).resolve()

    jpeg_parser = JpegParser()

    #read jpeg file
    if not jpeg_parser.read_jpeg_file(jpeg_file):
        print(f"ERROR: Could not access jpeg data: '{jpeg_file}'!")
        sys.exit(10)

    #data handling
    investigation_info = InvestigationInfo()
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

    if not ext_segs == None:
        extraction_dir = ext_dir / jpeg_file.stem
        if extraction_dir.exists() and not force_overwrite:
            print(f"ERROR: Directory at '{extraction_dir}' does already exist! Try running with '--force' option.")
            sys.exit(12)
        if not extraction_dir.exists():
            extraction_dir.mkdir(parents=True, exist_ok=True)

        filtered_segments = investigation_info.filter_segments_view(ext_segs)
        for seg_dat in filtered_segments:
            with open(extraction_dir / f"{seg_dat['id']}.blob", "wb") as file_handle:
                file_handle.write(jpeg_parser.get_jpeg_bytes()[seg_dat["fr"]:seg_dat["to"]])

    #done

    investigation_info_dict = investigation_info.__dict__

    structure_views = JpegInvestigationViewer(jpeg_parser.get_jpeg_bytes(), investigation_info_dict)
    complete_dict[str(jpeg_file)] = investigation_info_dict

    #draw report
    if not has_to_be_silent:
        print(structure_views.draw_report())
#save as json file
if not json_file == None:
    parent_dir = json_file.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)
    if json_file.exists() and not force_overwrite:
        print(f"ERROR: File at '{json_file}' does already exist! Try running with '--force' option.")
        sys.exit(12)
    with open(json_file, "w") as file_handle:
        file_handle.write(json.dumps(complete_dict, indent=2))

sys.exit(0)
