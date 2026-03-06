"""API Gateway infrastructure stack."""
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as lambda_
)
from constructs import Construct
from .compute_stack import ComputeStack


class ApiStack(Stack):
    """API infrastructure for OrchestRAI."""
    
    def __init__(self, scope: Construct, construct_id: str, compute_stack: ComputeStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create REST API
        api = apigw.RestApi(
            self, "OrchestRAIApi",
            rest_api_name="OrchestRAI Video Engine API",
            description="API for OrchestRAI video generation service",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        
        # Create API key
        api_key = api.add_api_key("ApiKey")
        
        # Create usage plan
        usage_plan = api.add_usage_plan(
            "UsagePlan",
            name="Standard",
            throttle=apigw.ThrottleSettings(
                rate_limit=100,
                burst_limit=200
            )
        )
        usage_plan.add_api_key(api_key)
        usage_plan.add_api_stage(stage=api.deployment_stage)
        
        # Upload endpoint
        upload_integration = apigw.LambdaIntegration(
            compute_stack.upload_handler,
            proxy=True
        )
        
        api_v1 = api.root.add_resource("api").add_resource("v1")
        upload_resource = api_v1.add_resource("upload")
        upload_resource.add_method(
            "POST",
            upload_integration,
            api_key_required=True
        )
        
        # Status endpoint
        status_integration = apigw.LambdaIntegration(
            compute_stack.status_handler,
            proxy=True
        )
        
        status_resource = api_v1.add_resource("status").add_resource("{workflowId}")
        status_resource.add_method(
            "GET",
            status_integration,
            api_key_required=True
        )
        
        # Video retrieval endpoint
        video_integration = apigw.LambdaIntegration(
            compute_stack.video_retrieval_handler,
            proxy=True
        )
        
        video_resource = api_v1.add_resource("video").add_resource("{videoId}")
        video_resource.add_method(
            "GET",
            video_integration,
            api_key_required=True
        )
        
        # Output API endpoint
        self.api_url = api.url
