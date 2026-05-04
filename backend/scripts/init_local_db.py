"""Create the single DynamoDB table for local development.

Usage:
    uv run python scripts/init_local_db.py

Requires DynamoDB Local to be running (docker-compose up).
"""

from __future__ import annotations

import asyncio
import os

import aioboto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "monopoly")
ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL", "http://localhost:8002")
REGION = os.environ.get("AWS_REGION", "us-east-1")


async def create_table() -> None:
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=REGION,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    ) as ddb:
        try:
            table = await ddb.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {"AttributeName": "PK", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "PK", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            await table.wait_until_exists()
            print(f"✓ Table '{TABLE_NAME}' created at {ENDPOINT_URL}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                print(f"✓ Table '{TABLE_NAME}' already exists — skipping")
            else:
                raise


if __name__ == "__main__":
    asyncio.run(create_table())
