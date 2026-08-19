import aws_cdk as cdk

from infrastructure.backend_stack import BackendStack
from infrastructure.database_stack import DatabaseStack
from infrastructure.frontend_stack import FrontendStack

app = cdk.App()

database_stack = DatabaseStack(
    app,
    "DatabaseStack",
)

backend_stack = BackendStack(
    app,
    "BackendStack",
    games_table=database_stack.games_table,
)

frontend_stack = FrontendStack(
    app,
    "FrontendStack",
    http_api=backend_stack.http_api,
    websocket_api=backend_stack.websocket_api,
)

app.synth()
