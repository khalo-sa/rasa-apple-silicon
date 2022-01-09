set -e

RASA_VERSION=${1:-3.0.4}

docker build \
    -t "rasa-aarch64:conda-${RASA_VERSION}" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    -f Dockerfile.conda .

docker build \
    -t "rasa-aarch64:${RASA_VERSION}" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    -f Dockerfile .