# Install Rasa on Macs with Apple Silicon 

As of December 2021, Rasa is not officially supported on Macs with ARM-based Apple Silicon processors. The solution described here should only be used as a (hacky) workaround until official support arrives.

It creates an Anaconda environment, and installs as many dependencies from Pip as possible based on the `pyproject.toml` of a specific Rasa Version, e.g. [3.0.3](https://github.com/RasaHQ/rasa/blob/3.0.3/pyproject.toml). All others are fetched from the `conda-forge` and `apple` Anaconda channels.

Most notably, Tensorflow is installed as described in [Apple's official documentation](https://developer.apple.com/metal/tensorflow-plugin/).

At the time of writing, the only dependency that could neither be  satisfied from Pip nor Anaconda is `tensorflow-text`. Therefore, projects that rely on Rasa features utiliing tensorflow-text will not work.

## Requirements

You need to have the arm64 (Apple Silicon) version of [Miniforge](https://github.com/conda-forge/miniforge) installed. Follow the installation steps on the linked Github page.

## Installation

Create a new Python-environment based on one of the environment files in this repo. For instance, to install Rasa 3.0.3 run this command:

```bash
conda env create --force -f https://raw.githubusercontent.com/khalo-sa/rasa-apple-silicon/main/3.0.3/environment.yml
```

This will take some time. Once the environment is created, activate it via:

```bash
conda activate rasa303
```

Now install the exact version of Rasa via Pip without its dependencies, and you should be done!

```bash
pip install --no-deps rasa==3.0.3
```

To verify that it's working, create a new project via `rasa init`, and train it via `rasa train`.



