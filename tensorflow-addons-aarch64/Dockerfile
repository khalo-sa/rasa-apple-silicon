FROM python:3.10 as builder

RUN pip install tensorflow-aarch64==2.11.0

RUN apt-get update \
    && apt-get install build-essential wget rsync -y

WORKDIR /tmp

RUN wget https://github.com/bazelbuild/bazel/releases/download/5.2.0/bazel-5.2.0-linux-arm64 \
    && chmod +x /tmp/bazel-5.2.0-linux-arm64 \
    && mv /tmp/bazel-5.2.0-linux-arm64 /usr/bin/bazel \
    && bazel version

RUN git clone --depth 1 --branch v0.19.0 https://github.com/tensorflow/addons.git /tmp/addons

WORKDIR /tmp/addons

RUN python ./configure.py

RUN bazel build build_pip_pkg
RUN bazel-bin/build_pip_pkg artifacts

FROM alpine:latest

WORKDIR /build

COPY --from=builder /tmp/addons/artifacts/tensorflow_addons-*.whl ./ 