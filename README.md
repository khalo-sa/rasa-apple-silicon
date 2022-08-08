# Rasa on Macs with Apple Silicon (Native / Docker)

As of July 2022, Rasa is not officially supported on Macs with ARM-based Apple Silicon processors.
The solution described here should only be used as a workaround until official support arrives.
It has been tested on a Macbook Pro with M1 Processor.

Docker, and native installation is supported. In both cases an Anaconda environment is created in which as many dependencies as possible are installed via `pip` based on the `pyproject.toml` of a specific Rasa release.
The remaining packages for which no `arm64`/`aarch64` wheels are available on PyPI are fetched from Anaconda channels (`conda-forge`, `noarch`, and `apple`) or from Github repositories that offer precompiled wheels.

At the time of writing, the only dependency that could neither be satisfied from Pip nor Anaconda is `tensorflow-text`.
Therefore, projects that rely on Rasa features utilizing this package will not work.

## Getting Started

Two installation methods are supported, Docker and Native. The supported Rasa versions for each method are:

- Docker: `3.0.9`, `3.1.0`, `3.2.1`, `3.2.5`
- Native: `3.2.1`

As a first step, you should store a supported version in an environment variable:

```bash
export RASA_VERSION="3.2.5"
```

Then proceed with one of the two methods.

### Docker

The easiest way to get started is by using the [Docker images on Dockerhub](https://hub.docker.com/r/khalosa/rasa-aarch64).

```bash
docker run -it --rm khalosa/rasa-aarch64:${RASA_VERSION}
```

Alternatively, if you want to build the image yourself:

```bash
./build-docker.sh
```

### Native Installation

If you want to run Rasa natively on your Mac, you need to have these tools installed:

- [Miniforge](https://github.com/conda-forge/miniforge), arm64 (Apple Silicon) version
- Python 3 (`pip`, and `python` commands must point to a Python3 installation)

Now run this snippet in the root directory of the project:

```bash
# use the generator script to create a conda env file
python -m rasa_dc --platform native --rasa_version $RASA_VERSION

# use the env file to create a new conda environment
conda env create --name rasa-${RASA_VERSION} --file=output/rasa_${RASA_VERSION}_native_env.yml

# finally install Rasa without dependencies into the newly created conda environment
$HOME/miniforge3/envs/rasa-$RASA_VERSION/bin/pip install --no-deps rasa==$RASA_VERSION
```

Now you should be able to activate the created environment:

```bash
conda activate rasa-${RASA_VERSION}
```

Verify that its working by executing `rasa init`.
