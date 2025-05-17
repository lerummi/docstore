FROM quay.io/jupyter/minimal-notebook:python-3.12

LABEL maintainer="Marta Krause <martin.krause.85@gmx.de>"

USER root

# Install apt packages
RUN apt-get update && \
    apt-get install -y git && \
    pip install --upgrade pip

USER ${NB_UID}

# Requirements are installed here to ensure they will be cached.
COPY --chown=${NB_UID}:${NB_UID} pyproject.toml pyproject.toml
COPY --chown=${NB_UID}:${NB_UID} poetry.lock poetry.lock

# Install Python 3 packages
RUN pip install poetry
RUN poetry self add poetry-plugin-export && poetry export -o /tmp/requirements.txt --without-hashes

RUN pip install --user --use-deprecated=legacy-resolver  -r /tmp/requirements.txt