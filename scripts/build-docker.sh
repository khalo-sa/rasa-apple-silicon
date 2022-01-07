set -e

# docker build -t rasa-aarch64 -f Dockerfile.conda .

RASA_VERSION="3.0.4"

docker build \
    -t "rasa:${RASA_VERSION}-aarch64" \
    --build-arg RASA_VERSION=${RASA_VERSION} \
    -f Dockerfile .
