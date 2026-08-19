from aws_cdk import Stack
from aws_cdk import (
    aws_cloudfront as cloudfront,
)
from aws_cdk import (
    aws_cloudfront_origins as origins,
)
from aws_cdk import (
    aws_s3 as s3,
)


class FrontendStack(Stack):
    def __init__(
        self,
        scope,
        construct_id,
        http_api,
        websocket_api,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "FrontendBucket",
        )

        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket),
            ),
        )

        # /api/*
        distribution.add_behavior(
            "/api/*",
            origins.HttpOrigin(http_api.url.replace("https://", "").rstrip("/")),
            allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
        )
