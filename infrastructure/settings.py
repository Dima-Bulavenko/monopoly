import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("ENV", "prod")


@dataclass
class Settings:
    env: Literal["prod"] = field(default="prod", init=False)


@dataclass
class BackendSettings(Settings):
    apigw_management_endpoint: str
    dynamodb_table_name: str
    aws_region: str = field(default_factory=lambda: os.environ.get("AWS_REGION", "eu-west-1"), init=False)

    database_url: str = field(
        default_factory=lambda: os.environ["DATABASE_URL"], init=False
    )

    jwt_private_key: str = field(
        default_factory=lambda: Path(
            os.environ["JWT_PRIVATE_KEY_PEM_PATH"]
        ).read_text(),
        init=False,
    )
    jwt_public_key: str = field(
        default_factory=lambda: Path(os.environ["JWT_PUBLIC_KEY_PEM_PATH"]).read_text(),
        init=False,
    )

    google_client_id: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLIENT_ID", ""), init=False
    )
    apple_client_id: str = field(
        default_factory=lambda: os.environ.get("APPLE_CLIENT_ID", ""), init=False
    )
