#!/bin/bash

if [ "$#" != "1" ]; then
    echo "Syntax: ./classify-segment-contents.sh <segments: csv>"
    echo "  e.g.: ./classify-segment-contents.sh dqt"
    echo "        ./classify-segment-contents.sh dqt,sof"
    exit 1
fi

cd "./workdir"
files=`ls *.jpg`
cd "../"

echo "JPEG investigator is running..."

./investigate-jpeg -ed segment-classifier -es "$1" -f -s $files
err_lvl=$?

if [ "$err_lvl" != "0" ]; then
    echo "ERROR: JPEG investigator exited with a non-zero error-code!"
    exit $err_lvl
fi

if [ ! -d "./workdir/segment-classifier" ]; then
    echo "ERROR: No data source available!"
    exit 20
fi

echo "Running classification..."

out_dir="./workdir/segment-classifier-hashmap"
if [ -d "${out_dir}" ]; then
    rm -drf $out_dir
fi
mkdir $out_dir

# loop segments
find "./workdir/segment-classifier" -mindepth 1 -maxdepth 1 -type d -print0 | 
    while IFS= read -r -d "" line; do
        identifier=$(echo $line | cut -d/ -f4)

        jpg_file="./workdir/${identifier}.jpg"
        if [ ! -f "${jpg_file}" ]; then
            echo "ERROR: Could not find '${jpg_file}'!"
            exit 21
        fi

        # read extracted segments
        sqt_path="./workdir/segment-classifier/${identifier}"
        segments=$(ls ./workdir/segment-classifier/${identifier}/*.blob)
        
        # copy all segments in one file, in order
        cat $segments > "./workdir/segment-classifier/${identifier}/_segments.blob"

        # calculate checksum
        checksum=$(shasum "./workdir/segment-classifier/${identifier}/_segments.blob" | cut -d " " -f1)

        # copy
        checksum_dir="${out_dir}/${checksum}"
        if [ ! -d "${checksum_dir}" ]; then
            echo "new class: ${checksum}"
            mkdir $checksum_dir
        fi

        checksum_file="${checksum_dir}/${identifier}.jpg"
        echo "classified ${jpg_file} as ${checksum}"
        cp "${jpg_file}" "${checksum_file}"
        echo " --> ${checksum_file}"
    done

echo "Done!"

exit 0
