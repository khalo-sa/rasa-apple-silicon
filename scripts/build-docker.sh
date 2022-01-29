set -e

RASA_VERSION=${RASA_VERSION:-3.0.5}

docker build \
    --target conda \
    -t "rasa-aarch64:conda-${RASA_VERSION}" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    .

docker build \
    -t "rasa-aarch64:${RASA_VERSION}" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    .