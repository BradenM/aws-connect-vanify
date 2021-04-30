FROM python:3.8 AS build

# Python Envs
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /wheels
COPY pyproject.toml poetry.lock* /wheels/

# Build wheel.
RUN poetry install --no-root \
    && poetry export \
        --without-hashes \
        -o requirements.txt \
    && pip wheel -r requirements.txt \
    && rm pyproject.toml \
    && rm poetry.lock*


FROM public.ecr.aws/lambda/python:3.8

# Install dependencies from wheels
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -f /wheels/ -r /wheels/requirements.txt \
  && rm -rf /wheels

COPY app.py ./

# You can overwrite command in `serverless.yml` template
CMD ["app.handler"]
