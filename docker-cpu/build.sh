set -e

# docker build -t rasa-aarch64 -f Dockerfile.conda .
docker build -t rasa:304-aarch64 -f Dockerfile .

