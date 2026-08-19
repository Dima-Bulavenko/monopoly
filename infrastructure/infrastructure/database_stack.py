from aws_cdk import (
    Stack,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.games_table = dynamodb.Table(
            self,
            "GamesTable",
            partition_key=dynamodb.Attribute(
                name="game_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
