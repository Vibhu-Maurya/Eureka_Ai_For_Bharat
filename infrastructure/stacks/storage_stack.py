"""Storage infrastructure stack (S3 + DynamoDB)."""
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class StorageStack(Stack):
    """Storage infrastructure for OrchestRAI."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 Buckets
        self.uploads_bucket = s3.Bucket(
            self, "UploadsBucket",
            bucket_name="orchestrai-uploads",
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldUploads",
                    expiration=Duration.days(30)
                )
            ]
        )
        
        self.content_bucket = s3.Bucket(
            self, "ContentBucket",
            bucket_name="orchestrai-content",
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteTempFiles",
                    prefix="temp/",
                    expiration=Duration.days(7)
                ),
                s3.LifecycleRule(
                    id="DeleteDrafts",
                    prefix="drafts/",
                    expiration=Duration.days(30)
                )
            ]
        )
        
        # DynamoDB Tables
        self.content_metadata_table = dynamodb.Table(
            self, "ContentMetadataTable",
            table_name="OrchestRAI-ContentMetadata",
            partition_key=dynamodb.Attribute(
                name="contentId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.workflow_state_table = dynamodb.Table(
            self, "WorkflowStateTable",
            table_name="OrchestRAI-WorkflowState",
            partition_key=dynamodb.Attribute(
                name="workflowId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.script_versions_table = dynamodb.Table(
            self, "ScriptVersionsTable",
            table_name="OrchestRAI-ScriptVersions",
            partition_key=dynamodb.Attribute(
                name="scriptId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="version",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.translations_table = dynamodb.Table(
            self, "TranslationsTable",
            table_name="OrchestRAI-Translations",
            partition_key=dynamodb.Attribute(
                name="translationId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="language",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.scene_plans_table = dynamodb.Table(
            self, "ScenePlansTable",
            table_name="OrchestRAI-ScenePlans",
            partition_key=dynamodb.Attribute(
                name="scenePlanId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.quality_evaluations_table = dynamodb.Table(
            self, "QualityEvaluationsTable",
            table_name="OrchestRAI-QualityEvaluations",
            partition_key=dynamodb.Attribute(
                name="evaluationId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.final_videos_table = dynamodb.Table(
            self, "FinalVideosTable",
            table_name="OrchestRAI-FinalVideos",
            partition_key=dynamodb.Attribute(
                name="videoId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="language",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
