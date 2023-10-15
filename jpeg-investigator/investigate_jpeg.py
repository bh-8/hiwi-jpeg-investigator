import argparse
import json
import pathlib
import sys

from jpeg_parser.jpeg_parser import JpegParser

parser = argparse.ArgumentParser(
    prog="./investigate-jpeg",
    description="JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection",
    epilog=None
)

parser.add_argument("jpeg_file")
args = parser.parse_args()

jpeg_file = pathlib.Path(args.jpeg_file).resolve()
jpeg_parser = JpegParser()

if not jpeg_parser.read_jpeg_file(jpeg_file):
    print(f"ERROR: Could not access jpeg data: '{jpeg_file}'!")
    sys.exit(10)

if not jpeg_parser.parse():
    print(f"ERROR: Mature error due jpeg parsing; make sure the provided data is in jpeg format!")
    sys.exit(11)

debug_output = json.dumps(jpeg_parser.complete_dict(), indent=4)

print(debug_output)

sys.exit(0)
