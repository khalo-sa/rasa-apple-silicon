FROM condaforge/miniforge3:latest as conda

ARG RASA_VERSION="3.0.5"

RUN apt update && apt install curl build-essential -y

# install bazel to build dm-tree
# from https://github.com/KumaTea/tensorflow-aarch64/blob/docker/docker/py38/Dockerfile
RUN set -ex \
    && cd /tmp \
    && wget https://github.com/bazelbuild/bazel/releases/download/3.7.2/bazel-3.7.2-linux-arm64 \
    && chmod +x /tmp/bazel-3.7.2-linux-arm64 \
    && mv /tmp/bazel-3.7.2-linux-arm64 /usr/bin/bazel \
    && bazel version

WORKDIR /app

COPY ./output/docker/rasa_${RASA_VERSION}_env.yml ./env.yml

# Create the virtual environment according to the env.yml file
# and install Rasa without its dependencies
RUN conda env create --file=./env.yml --name=rasa \
    && /opt/conda/envs/rasa/bin/pip install --no-deps rasa==${RASA_VERSION}

# https://pythonspeed.com/articles/activate-conda-dockerfile/
# SHELL ["conda", "run", "-n", "rasa", "/bin/bash", "-c"]

RUN conda init && \
    echo "conda activate rasa" >> ~/.bashrc

ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

ENTRYPOINT ["/bin/bash"]

FROM conda as builder

RUN conda install conda-pack

# Use conda-pack to create a standalone env:
RUN conda-pack --ignore-missing-files --name rasa -o /tmp/env.tar \
    && mkdir /opt/venv \
    && tar xf /tmp/env.tar -C /opt/venv \
    && rm /tmp/env.tar \
    && /opt/venv/bin/conda-unpack

FROM ubuntu:20.04 as runner

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/lib/aarch64-linux-gnu/libgomp.so.1 /usr/lib/aarch64-linux-gnu/libgomp.so.1

ENV PATH="/opt/venv/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

WORKDIR /app

ENTRYPOINT ["/bin/bash"]