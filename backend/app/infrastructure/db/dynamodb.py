"""DynamoDB client factory and table configuration."""

from __future__ import annotations

import os

import aioboto3

TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "monopoly")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

_session = aioboto3.Session()


def get_dynamodb_resource():
    """Return an async DynamoDB resource context manager."""
    return _session.resource(
        "dynamodb",
        region_name=AWS_REGION,
        endpoint_url=os.environ.get("DYNAMODB_ENDPOINT_URL"),  # for local dev
    )
