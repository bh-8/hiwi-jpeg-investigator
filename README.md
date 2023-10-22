# JPEG investigator
JPEG structure analysis tool featuring file integrity checks, segment extraction and stego detection.
## setup
### native installation from tarball
- extract `jpeg-investigator-release.tar.gz` to any location using `tar -xzf jpeg-investigator-release.tar.gz`
- open terminal in `jpeg-investigator-release/`
- run `./install` to install required dependencies natively
- execute `./investigate-jpeg --help` to double-check if installation was successful
### dockerized approach (no native installation)
- requires [docker engine](https://docs.docker.com/engine/install/ubuntu/)
- initiate build process using `./build`
- execute `./investigate-jpeg --help` to double-check if installation was successful
## usage
### JPEG investigator
- basic usage
    ```
    ./investigate-jpeg [-h] [-jf JSON_FILE] [-es EXTRACT_SEGMENTS] [-et]
                       [-ed EXTRACT_DIRECTORY] [-f] [-s]
                       jpeg_file [jpeg_file ...]
    ```
- parameters
    - `-jf <path>` or `--json_file <path>`: write investigation results as json file specified by `<path>`
    - `-es <segs>` or `--extract_segments <segs>`: extract one or more segment types specified by `<segs>`; possible values are e.g. `dqt` (targeting quantization tables), `dqt,dht,unknown` (targeting quantization tables, huffman tables and unknown data) or even `"*"` to extract all segments
    - `-et` or `--extract_thumbnails`: switch to enable thumbnail extraction
    - `-ed <path>` or `--extract_directory <path>`: specifies a directory `<path>` for segments and/or thumbnail(s) to be extracted to; therefore required when `-es` or `-et` is used
    - `-f` or `--force`: enable file overriding
    - `-s` or `--silent`: disable stdout; errors excluded
    - `jpeg_file [jpeg_file ...]`: one or more jpeg files to analyse
### utility scripts
- `./investigate-all`: uses all the tool's features to process every file in `./workdir/*.jpg`
- `./classify-all <segs>`: classifies all jpg files in `./workdir/*.jpg` based on given segment(s) `<segs>` using a hash map; possible values are e.g. `dqt` (targeting quantization tables) or `dqt,dht` (targeting quantization tables plus huffman tables)
    - **IMPORTANT**: when an image is classified it will be copied, so make sure there is enough storage available!
