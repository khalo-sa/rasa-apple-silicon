# Rasa on Macs with Apple Silicon (Native / Docker)

As of January 2022, Rasa is not officially supported on Macs with ARM-based Apple Silicon processors.
The solution described here should only be used as a workaround until official support arrives.
It has been tested on a Macbook Pro with M1 Processor.

Docker, and native installation is supported. In both cases an Anaconda environment is created, and as many dependencies from Pip as possible are installed based on the `pyproject.toml` of a specific Rasa Version, e.g. [3.0.3](https://github.com/RasaHQ/rasa/blob/3.0.3/pyproject.toml).
The remaining packages for which no `arm64`/`aarch64` wheels are available on PyPI are fetched from Anaconda channels (`conda-forge`, `noarch`, and `apple`).

At the time of writing, the only dependency that could neither be satisfied from Pip nor Anaconda is `tensorflow-text`.
Therefore, projects that rely on Rasa features utilizing tensorflow-text will not work.

## First steps

Clone this repo, then have a look inside the `output` directory.
The version numbers of the yaml files found inside `native`, and `docker` subdirectories
tell you which Rasa version you can currently install natively, or via Docker.
Choose a version and platform combination and then proceed to one of the next chapters.

## Native Installation

You need to have the arm64 (Apple Silicon) version of [Miniforge](https://github.com/conda-forge/miniforge) installed.
Follow the installation steps on the linked Github page.

Store the Rasa version of your choice in an environment variable.

```bash
export RASA_VERSION=3.0.4
```

Create a conda environment with the Rasa dependencies based on the .

```bash
conda env create --name rasa-${RASA_VERSION} --file=output/native/rasa_${RASA_VERSION}_env.yml
```

Activate it

```bash
conda activate rasa-${RASA_VERSION}
```

Finally, install Rasa without its dependencies (we already installed them).

```bash
pip install --no-deps rasa==${RASA_VERSION}
```

Verify that its working by executing `rasa init`.

## Docker

Store the Rasa version of your choice in an environment variable.

```bash
export RASA_VERSION=3.0.4
```

Run the build script.

```bash
./scripts/build-docker.sh
```

Start a container:

```bash
docker run -it rasa-aarch64:${RASA_VERSION} bash
```
