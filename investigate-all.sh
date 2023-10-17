#!/bin/bash

cd ./workdir
files=`ls *.jpg`
cd ../

./investigate-jpeg -ed full-processing -es "*" -et -jf full-processing/full-processing.json -f $files

exit 0
