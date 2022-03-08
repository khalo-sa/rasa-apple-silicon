# Rasa on Macs with Apple Silicon (Native / Docker)

As of March 2022, Rasa is not officially supported on Macs with ARM-based Apple Silicon processors.
The solution described here should only be used as a workaround until official support arrives.
It has been tested on a Macbook Pro with M1 Processor.

Docker, and native installation is supported. In both cases an Anaconda environment is created in which as many dependencies as possible are installed via `pip` based on the `pyproject.toml` of a specific Rasa release.
The remaining packages for which no `arm64`/`aarch64` wheels are available on PyPI are fetched from Anaconda channels (`conda-forge`, `noarch`, and `apple`) or from Github repositories that offer precompiled wheels.

At the time of writing, the only dependency that could neither be satisfied from Pip nor Anaconda is `tensorflow-text`.
Therefore, projects that rely on Rasa features utilizing this package will not work.

## Getting Started

### Docker

The easiest way to get started is by using the [Docker image](https://hub.docker.com/r/khalosa/rasa-aarch64).

```bash
docker run -it --rm khalosa/rasa-aarch64:latest
```

Choose one of the [available Rasa versions](/output/docker), and store it in an environment variable:

Alternatively, if you want to build the image yourself:

```bash
./scripts/build-docker.sh
```

### Native Installation

If you want to run Rasa natively on your Mac with GPU-support, you need to have these tools installed:

- [Miniforge](https://github.com/conda-forge/miniforge), arm64 (Apple Silicon) version
- Python 3

```bash
# set rasa version
export RASA_VERSION="3.0.8"

# use the small library in this repo to create a conda env file
python -m rasa_dc --platform native --rasa_version $RASA_VERSION

# create a new conda environment from the generated file
conda env create --name rasa-${RASA_VERSION} --file=output/rasa_${RASA_VERSION}_native_env.yml

# finally install Rasa without dependencies into the newly created conda environment
$HOME/miniforge3/envs/rasa-$RASA_VERSION/bin/pip install --no-deps rasa==$RASA_VERSION
```

Now you should be able to activate the created environment:

```bash
conda activate rasa-${RASA_VERSION}
```

Verify that its working by executing `rasa init`.
