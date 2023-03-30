# global variables
ARG RASA_VERSION
ARG USER="rasa"
ARG HOME="/app"
ARG VENV="/opt/venv"
ARG UID=1001
ARG GID=1001
ARG PYTHON_VERSION="3.10"

FROM condaforge/mambaforge:latest as conda

RUN apt-get update \
    && apt-get install build-essential -y

# for confluent-kafka
# https://github.com/confluentinc/confluent-kafka-python/issues/1326#issuecomment-1228852754
RUN apt-get install -y --no-install-recommends gcc git libssl-dev g++ make && \
    cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
    cd librdkafka && git checkout tags/v1.9.0 && \
    ./configure && make && make install && \
    cd ../ && rm -rf librdkafka

# use global variables
ARG USER
ARG HOME
ARG VENV
ARG UID
ARG GID
ARG RASA_VERSION
ARG PYTHON_VERSION

# create nonroot user with home directory ad /nonroot
RUN groupadd \
    --gid $GID \
    $USER \
    && useradd \
    --uid $UID \
    --gid $GID \
    --create-home \
    --home $HOME \
    $USER \
    && chown -R $USER $HOME

WORKDIR $HOME

ARG ENV_FILE="env-$RASA_VERSION.yaml"
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./rasa_dc ./rasa_dc
RUN python -m rasa_dc \
    --platform docker \
    --python $PYTHON_VERSION \
    --rasa_version $RASA_VERSION \
    -d "." \
    -f $ENV_FILE


# Create the virtual environment according to the env.yml file
COPY ./tensorflow-addons-aarch64/whl /tmp/tfa-whl
RUN conda env create \
    --file=$ENV_FILE \
    --prefix $VENV
RUN rm -rf /tmp/*

# make conda env default python env
ENV PATH="$VENV/bin:$PATH"
# ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

# install Rasa without dependencies
RUN pip install --no-deps rasa==${RASA_VERSION}

USER $USER

FROM ubuntu:20.04 as runner

# use global variables
ARG USER
ARG HOME
ARG VENV
ARG UID
ARG GID
ARG RASA_VERSION

# create nonroot user with home directory at /nonroot
RUN groupadd \
    --gid $GID \
    $USER \
    && useradd \
    --uid $UID \
    --gid $GID \
    --create-home \
    --home $HOME \
    $USER \
    && chown -R $USER $HOME

COPY --from=conda $VENV $VENV
# COPY --from=conda /usr/lib/aarch64-linux-gnu/libgomp.so.1.0.0 /usr/lib/aarch64-linux-gnu/libgomp.so.1.0.0

# fix for scikit learn
# ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1.0.0
# make conda env default python env
ENV PATH="$VENV/bin:$PATH"

WORKDIR $HOME

USER $USER

ENTRYPOINT ["rasa"]