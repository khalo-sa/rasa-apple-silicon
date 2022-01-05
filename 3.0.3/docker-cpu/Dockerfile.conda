FROM condaforge/miniforge3:latest

RUN apt update

RUN apt install curl build-essential -y
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH "/root/.poetry/bin:${PATH}"

ARG RASA_VERSION="3.0.4"

WORKDIR /app

RUN conda create --name rasa python=3.8

# https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "rasa", "/bin/bash", "-c"]
RUN conda init && \
    echo "conda activate rasa" >> ~/.bashrc

RUN set -ex \
    \
    && cd /tmp \
    && wget https://github.com/bazelbuild/bazel/releases/download/3.7.2/bazel-3.7.2-linux-arm64 \
    && chmod +x /tmp/bazel-3.7.2-linux-arm64 \
    && mv /tmp/bazel-3.7.2-linux-arm64 /usr/bin/bazel \
    && bazel version

COPY "./environment-${RASA_VERSION}-base.yml" ./environment.yml
RUN conda install --file environment.yml

COPY ./wheels/ ./wheels
RUN /opt/conda/envs/rasa/bin/pip install ./wheels/*

COPY "./pyproject-${RASA_VERSION}.toml" ./pyproject.toml
RUN poetry install --no-interaction --no-dev -vvv 
# --extras "transformers"

RUN export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

