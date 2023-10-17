# JPEG investigator
JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection.

## setup
### docker
- requires docker installation
- build image:
    ```
    ./build
    ```
- basic execution (help):
    ```
    ./investigate-jpeg -h
    ```
### native
- apt dependencies:
    ```
    apt-get update \
    && apt-get install -y \
    python3.10 python3-pip exiftool
    ```
    (`exiftool` is required to extract thumbnails)
- pip requirements:
    ```
    pip install --upgrade pip \
    && pip install texttable
    ```
- basic execution (help):
    ```
    python3 ./investigate_jpeg.py -h
    ```