#!/bin/bash

DOCKER_BUILDKIT=1 docker build \
    --tag birnbaum01/hiwi-jpeg-investigator \
    .

docker run --rm \
    --hostname="$(hostname)" \
    --volume=$(realpath ./workdir):/home/workdir \
    birnbaum01/hiwi-jpeg-investigator
