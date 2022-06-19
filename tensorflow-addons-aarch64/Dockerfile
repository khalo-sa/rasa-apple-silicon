FROM python:3.8 as builder

RUN pip install tensorflow-aarch64==2.7.3

RUN apt-get update \
    && apt-get install build-essential wget rsync -y

WORKDIR /tmp

RUN wget https://github.com/bazelbuild/bazel/releases/download/5.2.0/bazel-5.2.0-linux-arm64 \
    && chmod +x /tmp/bazel-5.2.0-linux-arm64 \
    && mv /tmp/bazel-5.2.0-linux-arm64 /usr/bin/bazel \
    && bazel version

RUN git clone https://github.com/tensorflow/addons.git /tmp/addons

WORKDIR /tmp/addons

RUN python ./configure.py

RUN bazel build build_pip_pkg
RUN bazel-bin/build_pip_pkg artifacts

FROM alpine:latest

WORKDIR /build

COPY --from=builder /tmp/addons/artifacts/tensorflow_addons-*.whl ./ 