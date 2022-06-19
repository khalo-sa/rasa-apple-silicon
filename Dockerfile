# global variables
ARG RASA_VERSION
ARG USER="nonroot"
ARG HOME="/nonroot"
ARG UID=1000
ARG GID=1000
ARG CONDA_ENV_NAME="rasa"
ARG CONDA_ENV="$HOME/.conda/envs/$CONDA_ENV_NAME"
ARG PYTHON_VERSION="3.8"

FROM condaforge/miniforge3:latest as conda

RUN apt-get update \
    && apt-get install build-essential -y

# use global variables
ARG USER
ARG HOME
ARG UID
ARG GID
ARG RASA_VERSION
ARG CONDA_ENV_NAME
ARG CONDA_ENV

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
    --rasa_version $RASA_VERSION \
    -d "." \
    -f $ENV_FILE

USER $USER

# Create the virtual environment according to the env.yml file
COPY ./tensorflow-addons-aarch64/whl ./tfa-whl
RUN conda env create \
    --file=$ENV_FILE \
    --name=$CONDA_ENV_NAME

ENV PATH="$CONDA_ENV/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

# install Rasa without dependencies
RUN pip install --no-deps rasa==${RASA_VERSION}

FROM ubuntu:20.04 as runner

# use global variables
ARG USER
ARG HOME
ARG UID
ARG GID
ARG CONDA_ENV
ARG RASA_VERSION

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

COPY --from=conda $CONDA_ENV $CONDA_ENV
COPY --from=conda /usr/lib/aarch64-linux-gnu/libgomp.so.1 /usr/lib/aarch64-linux-gnu/libgomp.so.1

ENV PATH="$CONDA_ENV/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

WORKDIR $HOME

USER $USER

ENTRYPOINT ["/bin/bash"]