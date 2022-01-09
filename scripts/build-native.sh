#!/bin/bash

set -e

RASA_VERSION=${1:-3.0.4}

# ensure "conda activate" works
conda init bash && source ~/.bash_profile

conda env create --name rasa-${RASA_VERSION} --file=output/native/rasa_${RASA_VERSION}_env.yml | true
conda activate rasa-${RASA_VERSION}
pip install --no-deps rasa==${RASA_VERSION}