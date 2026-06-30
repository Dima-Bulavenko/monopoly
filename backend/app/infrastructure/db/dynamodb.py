"""DynamoDB client factory and table configuration."""

from __future__ import annotations
from typing import TYPE_CHECKING, AsyncContextManager

import aioboto3

from app.config import settings

if TYPE_CHECKING:
    from types_aiobotocore_dynamodb.service_resource import DynamoDBServiceResource

TABLE_NAME = settings.dynamodb_table_name

_session = aioboto3.Session()


def get_dynamodb_resource() -> "AsyncContextManager[DynamoDBServiceResource]":
    """Return an async DynamoDB resource context manager."""
    return _session.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,  # for local dev
    )
