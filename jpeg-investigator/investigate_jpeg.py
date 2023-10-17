import argparse
import glob
import json
import os
import pathlib
import shutil
import subprocess
import sys

from jpeg_parser.parser import JpegParser
from data_handling import InvestigationInfo
from segment_views import JpegInvestigationViewer

INVESTIGATOR_VERSION = "2.4b"

# JPEG references
# https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
# https://help.accusoft.com/ImageGear/v18.8/Linux/IGDLL-10-05.html
# ps data id: https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/

#TODO list:
# verify outguess signature correctness


# initialize argument parser
arg_parser = argparse.ArgumentParser(
    prog="./investigate-jpeg",
    description=f"JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection.",
    epilog=f"JPEG investigator v{INVESTIGATOR_VERSION}"
)

# add arguments
arg_parser.add_argument("jpeg_file", nargs="+",         help="specify one or more JPEG files to process")
arg_parser.add_argument("-jf", "--json_file",           help="exports full investigation data to given json file")
arg_parser.add_argument("-es", "--extract_segments",    help="extract specified segments, e.g. 'app0,dqt,unknown' or '*'; requires '--extract_directory'")
arg_parser.add_argument("-et", "--extract_thumbnails",  help="extract thumbnails; requires '--extract_directory'", action="store_true")
arg_parser.add_argument("-ed", "--extract_directory",   help="set path to store extracted data")
arg_parser.add_argument("-f", "--force",                help="force file overwrite when exporting", action="store_true")
arg_parser.add_argument("-s", "--silent",               help="disable output on stdout", action="store_true")

args = arg_parser.parse_args()

# validate arguments
json_file = None if args.json_file is None else pathlib.Path(args.json_file).resolve()
extract_segments = None if args.extract_segments is None else args.extract_segments.lower()
extract_thumbnails = args.extract_thumbnails
extract_directory = None if args.extract_directory is None else pathlib.Path(args.extract_directory).resolve()
force_overwrite = args.force
has_to_be_silent = args.silent

if (extract_segments is not None and extract_directory is None):
    print(f"ERROR: Parameter '--extract_segments' requires '--extract_directory'!")
    sys.exit(10)
if (extract_thumbnails and extract_directory is None):
    print(f"ERROR: Parameter '--extract_thumbnails' requires '--extract_directory'!")
    sys.exit(10)

# start investigation phase
complete_dict = {}
for _jpeg_file in args.jpeg_file:
    jpeg_file = pathlib.Path(_jpeg_file).resolve()
    jpeg_parser = JpegParser()

    # read jpeg file
    if not jpeg_parser.read_jpeg_file(jpeg_file):
        print(f"ERROR: Could not access jpeg data: '{jpeg_file}'!")
        continue

    # data handling
    investigation_info = InvestigationInfo()
    investigation_info.set_initial_investigation_info(
        jpeg_file,
        len(jpeg_parser.get_jpeg_bytes()),
        INVESTIGATOR_VERSION
    )

    # parse jpeg file
    if not jpeg_parser.parse(investigation_info):
        print(f"ERROR: Mature error due jpeg parsing; make sure the provided data is in jpeg format!")
        continue

    # perform calculations after data acquisition
    investigation_info.determine_coverage()

    # extraction
    extract_count = 0

    if extract_segments is not None or extract_thumbnails:
        extraction_dir = extract_directory / jpeg_file.stem
        if extraction_dir.exists() and not force_overwrite:
            print(f"ERROR: Directory at '{extraction_dir}' does already exist! Try running with '--force' option.")
            continue
        if not extraction_dir.exists():
            extraction_dir.mkdir(parents=True, exist_ok=True)

    # export segments
    if extract_segments is not None:
        extraction_dir = extract_directory / jpeg_file.stem

        filtered_segments = investigation_info.filter_segments_view(extract_segments)
        for seg_dat in filtered_segments:
            with open(extraction_dir / f"{seg_dat['id']}.blob", "wb") as file_handle:
                file_handle.write(jpeg_parser.get_jpeg_bytes()[seg_dat["fr"]:seg_dat["to"]])
                extract_count += 1

    # thumbnail extraction
    if extract_thumbnails:
        extraction_dir = extract_directory / jpeg_file.stem
        if shutil.which("exiftool") is None:
            print(f"ERROR: Could not find 'exiftool' command. Is it installed and on path?")
            sys.exit(11)

        # remove existing thumbnails
        thumbnail_file = extraction_dir / 'thumbnail'
        [os.remove(f) for f in glob.glob(f"{thumbnail_file}*")]
        exifexec = [
            "exiftool",
            "-a",
            "-b",
            "-W",
            f"{thumbnail_file}-%t.%s",
            "-preview:all",
            str(jpeg_file)
        ]
        exifResultStr = subprocess.check_output(exifexec, stderr = subprocess.STDOUT).strip(b"\x20\n").decode(errors = "ignore")
        exifThumbnailNum = exifResultStr.split(" ")[0]

    # done, hand data to viewer
    structure_views = JpegInvestigationViewer(jpeg_parser.get_jpeg_bytes(), investigation_info.__dict__)
    complete_dict[str(jpeg_file)] = investigation_info.__dict__

    # draw report
    if not has_to_be_silent:
        print(structure_views.draw_report())
        if not extract_count == 0:
            print(f" > files extracted to '{extract_directory / jpeg_file.stem}'.")

#save as json file
if json_file is not None:
    parent_dir = json_file.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)
    if json_file.exists() and not force_overwrite:
        print(f"ERROR: File at '{json_file}' does already exist! Try running with '--force' option.")
        sys.exit(12)
    with open(json_file, "w") as file_handle:
        file_handle.write(json.dumps(complete_dict, indent=2))
        if not has_to_be_silent:
            print(f" > json file saved to '{json_file}'.")

sys.exit(0)
