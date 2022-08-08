#!/bin/bash

set -e

RASA_VERSION=${RASA_VERSION:-3.2.5}

docker build \
    --target conda \
    -t "khalosa/rasa-aarch64:conda-${RASA_VERSION}" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    .

docker build \
    -t "khalosa/rasa-aarch64:${RASA_VERSION}" \
    -t "khalosa/rasa-aarch64:latest" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    .
