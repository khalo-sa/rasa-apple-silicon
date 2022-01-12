ARG RASA_VERSION="3.0.4"

FROM "rasa-aarch64:conda-${RASA_VERSION}" as builder

RUN conda install conda-pack

# Use conda-pack to create a standalone env:
RUN conda-pack --ignore-missing-files --name rasa -o /tmp/env.tar \
    && mkdir /opt/venv \
    && tar xf /tmp/env.tar -C /opt/venv \
    && rm /tmp/env.tar \
    && /opt/venv/bin/conda-unpack

FROM ubuntu:20.04 as runner

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/lib/aarch64-linux-gnu/libgomp.so.1 /usr/lib/aarch64-linux-gnu/libgomp.so.1

ENV PATH="/opt/venv/bin:$PATH"
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

WORKDIR /app

ENTRYPOINT ["/bin/bash"]
