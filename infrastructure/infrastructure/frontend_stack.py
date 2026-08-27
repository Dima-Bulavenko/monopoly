from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_s3_deployment,
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

        api_origin_request_policy = cloudfront.OriginRequestPolicy(
            self,
            "ApiOriginRequestPolicy",
            cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
        )
        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_root_object="_shell.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/_shell.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/_shell.html",
                ),
            ],
        )

        # /api/*
        distribution.add_behavior(
            "/api/v1/*",
            origins.HttpOrigin(http_api.url.replace("https://", "").rstrip("/")),
            allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            origin_request_policy=api_origin_request_policy,
        )

        aws_s3_deployment.BucketDeployment(
            self,
            "FrontendDeployment",
            sources=[aws_s3_deployment.Source.asset("../frontend/dist/client")],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )
