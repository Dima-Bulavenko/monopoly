# backend_stack.py

from aws_cdk import (
    Stack,
)
from aws_cdk import (
    aws_apigatewayv2 as apigw,
)
from aws_cdk import (
    aws_apigatewayv2_integrations as integrations,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from constructs import Construct


class BackendStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        games_table,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        backend = lambda_.Function(
            self,
            "BackendFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=lambda_.Code.from_asset("../../backend"),
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
                backend,
            ),
        )

        # WebSocket API
        websocket_api = apigw.WebSocketApi(
            self,
            "WebSocketApi",
            connect_route_options=apigw.WebSocketRouteOptions(
                integration=integrations.WebSocketLambdaIntegration(
                    "ConnectIntegration",
                    backend,
                )
            ),
        )

        websocket_stage = apigw.WebSocketStage(
            self,
            "WebSocketStage",
            web_socket_api=websocket_api,
            stage_name="prod",
            auto_deploy=True,
        )

        self.http_api = http_api
        self.websocket_api = websocket_api
