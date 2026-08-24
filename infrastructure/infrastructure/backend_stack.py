from aws_cdk import (
    Duration,
    Stack,
)
from aws_cdk import (
    aws_apigatewayv2 as apigw,
)
from aws_cdk import (
    aws_apigatewayv2_integrations as integrations,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from constructs import Construct

from settings import BackendSettings


class BackendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        games_table: dynamodb.ITable,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # WebSocket API

        backend = lambda_.DockerImageFunction(
            self,
            "BackendFunction",
            code=lambda_.DockerImageCode.from_image_asset("../backend"),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # Give Lambda access to DynamoDB
        games_table.grant_read_write_data(backend)

        # HTTP API
        http_api = apigw.HttpApi(
            self,
            "HttpApi",
        )

        http_api.add_routes(
            path="/{proxy+}",
            methods=[apigw.HttpMethod.ANY],
            integration=integrations.HttpLambdaIntegration(
                "HttpIntegration",
                backend, # ty: ignore[invalid-argument-type]
            ),
        )

        websocket_api = apigw.WebSocketApi(
            self,
            "WebSocketApi",
            connect_route_options=apigw.WebSocketRouteOptions(
                integration=integrations.WebSocketLambdaIntegration(
                    "ConnectIntegration",
                    backend, # ty: ignore[invalid-argument-type]
                )
            ),
        )
        websocsket_stage = apigw.WebSocketStage(
            self,
            "WebSocketStage",
            web_socket_api=websocket_api,
            stage_name="prod",
            auto_deploy=True,
        )
        settings = BackendSettings(
            dynamodb_table_name=games_table.table_name,
            apigw_management_endpoint=websocsket_stage.callback_url,
        )
        backend.add_environment("ENV", settings.env)
        backend.add_environment("DYNAMODB_TABLE_NAME", settings.dynamodb_table_name)
        backend.add_environment("APIGW_MANAGEMENT_ENDPOINT", settings.apigw_management_endpoint)
        backend.add_environment("DATABASE_URL", settings.database_url)
        backend.add_environment("JWT_PRIVATE_KEY_PEM_PATH", settings.jwt_private_key)
        backend.add_environment("JWT_PUBLIC_KEY_PEM_PATH", settings.jwt_public_key)
        backend.add_environment("GOOGLE_CLIENT_ID", settings.google_client_id)
        backend.add_environment("APPLE_CLIENT_ID", settings.apple_client_id)
        self.http_api = http_api
        self.websocket_api = websocket_api
