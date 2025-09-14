#!/usr/bin/bash

IMAGE=fsprot-test

docker container rm -f $IMAGE > /dev/null

docker build -t $IMAGE .

docker run \
    --name $IMAGE \
    --tty \
    --interactive \
    $IMAGE
