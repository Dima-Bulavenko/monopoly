ARG UV_VERSION=0.10.7
ARG PYTHON_VERSION=3.14

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION} AS base

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

ARG PYTHON_VERSION

COPY --from=build-lambda ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="${VIRTUAL_ENV}/bin:$PATH" \
    PYTHONPATH="${VIRTUAL_ENV}/lib/python${PYTHON_VERSION}/site-packages"

COPY ./app ./app

CMD [ "app.aws_handler.lambda_handler" ]
