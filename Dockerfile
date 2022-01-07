FROM condaforge/miniforge3:latest

ARG RASA_VERSION="3.0.4"

RUN apt update && apt install curl build-essential -y

# install bazel to build dm-tree
RUN set -ex \
    && cd /tmp \
    && wget https://github.com/bazelbuild/bazel/releases/download/3.7.2/bazel-3.7.2-linux-arm64 \
    && chmod +x /tmp/bazel-3.7.2-linux-arm64 \
    && mv /tmp/bazel-3.7.2-linux-arm64 /usr/bin/bazel \
    && bazel version

WORKDIR /app

COPY ./output/rasa_${RASA_VERSION}_env.yml ./env.yml
COPY ./wheels/ /wheels

RUN conda env create --name rasa --file=./env.yml

# https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "rasa", "/bin/bash", "-c"]
RUN conda init && \
    echo "conda activate rasa" >> ~/.bashrc && \
    echo "export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1" >> ~/.bashrc

RUN pip install --no-deps rasa==${RASA_VERSION}
