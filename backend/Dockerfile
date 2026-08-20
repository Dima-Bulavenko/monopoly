ARG UV_VERSION=0.10.7
ARG PYTHON_VERSION=0.10.7

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION} AS base

WORKDIR /code

ENV VIRTUAL_ENV="/venvs/.venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"



FROM base AS build-lambda

COPY --from=uv /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=${VIRTUAL_ENV} \
    UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project


FROM base AS lambda

COPY --from=build-lambda ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ENV PYTHONDONTWRITEBYTECODE=1 \
    # Turns off buffering for easier container logging
    PYTHONUNBUFFERED=1 \
    PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY ./app ./app

ENTRYPOINT [ "python", "-m", "awslambdaric" ]

CMD [ "app.aws_handler.lambda_handler" ]
