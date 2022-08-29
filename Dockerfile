# global variables
ARG RASA_VERSION
ARG USER="rasa"
ARG HOME="/app"
ARG VENV="/opt/venv"
ARG UID=1001
ARG GID=1001
ARG PYTHON_VERSION="3.8"

FROM condaforge/miniforge3:latest as conda

RUN apt-get update \
    && apt-get install build-essential -y

# use global variables
ARG USER
ARG HOME
ARG VENV
ARG UID
ARG GID
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


# Create the virtual environment according to the env.yml file
COPY ./tensorflow-addons-aarch64/whl /tmp/tfa-whl
RUN conda env create \
    --file=$ENV_FILE \
    --prefix $VENV
RUN rm -rf /tmp/*

# make conda env default python env
ENV PATH="$VENV/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

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

COPY --from=conda $VENV $VENV
COPY --from=conda /usr/lib/aarch64-linux-gnu/libgomp.so.1 /usr/lib/aarch64-linux-gnu/libgomp.so.1

# make conda env default python env
ENV PATH="$VENV/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

WORKDIR $HOME

USER $USER

ENTRYPOINT ["/bin/bash"]