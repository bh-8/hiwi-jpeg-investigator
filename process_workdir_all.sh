#!/bin/bash

for i in ./workdir/*.jpg; do
    file_name=$(echo $i | cut -d/ -f3)
    ./investigate-jpeg -ed full_processing -es "*" -et -jf full_processing/$file_name.json -f $file_name
done

exit 0
