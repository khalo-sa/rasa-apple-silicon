# Rasa Docker image for Macs with Apple Silicon (aarch64)

As of November 2022, the official Rasa Docker image [is not compatible with ARM-based Macs](https://rasa.com/docs/rasa/installation/environment-set-up/#m1--m2-apple-silicon-limitations).
The solution described here should only be used as a workaround until official support arrives.
It has been tested on a Macbook Pro with M1 Processor, but might also work on other ARM-based machines like the Raspberry Pi.

At the time of writing, the only dependency that could neither be satisfied from Pip nor Anaconda is `tensorflow-text`.
Therefore, projects that rely on Rasa features utilizing this package will not work.

## Getting Started

The easiest way to get started is by using one of the available [images on Dockerhub](https://hub.docker.com/r/khalosa/rasa-aarch64):

- `khalosa/rasa-aarch64:3.0.9`
- `khalosa/rasa-aarch64:3.1.0`
- `khalosa/rasa-aarch64:3.2.1`
- `khalosa/rasa-aarch64:3.2.5`
- `khalosa/rasa-aarch64:3.3.1`

```bash
docker run -it --rm khalosa/rasa-aarch64:3.3.1
```

Alternatively, if you want to build the image yourself:

```bash
RASA_VERSION="3.3.1" ./build-docker.sh
```
