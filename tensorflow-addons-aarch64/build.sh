#!/bin/sh

set -ex

IMAGE="tfa-aarch64-builder:latest"

docker build \
    -t $IMAGE \
    .

docker run \
    --rm \
    -v "$PWD/whl:/host" \
    $IMAGE \
    sh -c "cp /build/* /host"