"""Compute infrastructure stack (Lambda + Step Functions)."""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    Fn,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam as iam,
    aws_logs as logs
)
from constructs import Construct
from .storage_stack import StorageStack


class ComputeStack(Stack):
    """Compute infrastructure for OrchestRAI."""
    
    def __init__(self, scope: Construct, construct_id: str, storage_stack: StorageStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Common Lambda execution role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant permissions to Lambda role
        storage_stack.uploads_bucket.grant_read_write(lambda_role)
        storage_stack.content_bucket.grant_read_write(lambda_role)
        storage_stack.content_metadata_table.grant_read_write_data(lambda_role)
        storage_stack.workflow_state_table.grant_read_write_data(lambda_role)
        storage_stack.script_versions_table.grant_read_write_data(lambda_role)
        storage_stack.quality_evaluations_table.grant_read_write_data(lambda_role)
        
        # Grant Bedrock invocation and marketplace permissions
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "bedrock:InvokeModel",
                # some Bedrock models require marketplace subscription actions
                "aws-marketplace:ViewSubscriptions",
                "aws-marketplace:Subscribe",
            ],
            resources=["*"]
        ))
        
        # Grant Transcribe permissions
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob"
            ],
            resources=["*"]
        ))
        
        # Upload Handler Lambda
        self.upload_handler = lambda_.Function(
            self, "UploadHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/upload_handler"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "UPLOADS_BUCKET": storage_stack.uploads_bucket.bucket_name,
                "CONTENT_METADATA_TABLE": storage_stack.content_metadata_table.table_name
            }
        )
        
        # Expose lambda role for workflow stack
        self.lambda_role = lambda_role
        
        # Transcript Extractor Lambda
        self.transcript_extractor = lambda_.Function(
            self, "TranscriptExtractor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/transcript_extractor"),
            timeout=Duration.minutes(15),
            memory_size=1024,
            role=lambda_role,
            environment={
                "CONTENT_BUCKET": storage_stack.content_bucket.bucket_name,
                "WORKFLOW_STATE_TABLE": storage_stack.workflow_state_table.table_name
            }
        )
        
        # Script Generator Lambda
        self.script_generator = lambda_.Function(
            self, "ScriptGenerator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/script_generator"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                "SCRIPT_VERSIONS_TABLE": storage_stack.script_versions_table.table_name
            }
        )
        
        # AI Critic Lambda
        self.ai_critic = lambda_.Function(
            self, "AICritic",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/ai_critic"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                "QUALITY_EVALUATIONS_TABLE": storage_stack.quality_evaluations_table.table_name
            }
        )
        
        # Translation Service Lambda
        self.translation_service = lambda_.Function(
            self, "TranslationService",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/translation_service"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                "TRANSLATIONS_TABLE": storage_stack.translations_table.table_name,
                "SCRIPT_VERSIONS_TABLE": storage_stack.script_versions_table.table_name,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0"
            }
        )
        
        # Scene Planner Lambda
        self.scene_planner = lambda_.Function(
            self, "ScenePlanner",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/scene_planner"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                "SCENE_PLANS_TABLE": storage_stack.scene_plans_table.table_name,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0"
            }
        )
        
        # Voice Synthesizer Lambda
        self.voice_synthesizer = lambda_.Function(
            self, "VoiceSynthesizer",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/voice_synthesizer"),
            timeout=Duration.minutes(10),
            memory_size=1024,
            role=lambda_role,
            environment={
                "CONTENT_BUCKET": storage_stack.content_bucket.bucket_name,
                "TRANSLATIONS_TABLE": storage_stack.translations_table.table_name
            }
        )
        
        # Grant Polly permissions
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["polly:SynthesizeSpeech"],
            resources=["*"]
        ))
        
        # Video Assembler Lambda
        # Note: This requires FFmpeg Lambda layer to be deployed separately
        # For now, we'll create the function and add the layer ARN later
        self.video_assembler = lambda_.Function(
            self, "VideoAssembler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/video_assembler"),
            timeout=Duration.minutes(15),  # Video processing can take time
            memory_size=3008,  # Maximum memory for better performance
            ephemeral_storage_size=cdk.Size.mebibytes(10240),  # 10GB for video processing
            role=lambda_role,
            environment={
                "CONTENT_BUCKET": storage_stack.content_bucket.bucket_name,
                "SCENE_PLANS_TABLE": storage_stack.scene_plans_table.table_name,
                "FFMPEG_PATH": "/opt/bin/ffmpeg",
                "FFPROBE_PATH": "/opt/bin/ffprobe"
            }
        )
        
        # Completion Handler Lambda
        self.completion_handler = lambda_.Function(
            self, "CompletionHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/completion_handler"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "CONTENT_BUCKET": storage_stack.content_bucket.bucket_name,
                "FINAL_VIDEOS_TABLE": storage_stack.final_videos_table.table_name,
                "WORKFLOW_STATE_TABLE": storage_stack.workflow_state_table.table_name
            }
        )
        
        # Status Handler Lambda
        self.status_handler = lambda_.Function(
            self, "StatusHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="status_handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/api_handlers"),
            timeout=Duration.seconds(10),
            memory_size=256,
            role=lambda_role,
            environment={
                "WORKFLOW_STATE_TABLE": storage_stack.workflow_state_table.table_name,
                "STEP_FUNCTIONS_ARN": Fn.import_value("OrchestRAI-StateMachineArn")
            }
        )
        
        # Video Retrieval Handler Lambda
        self.video_retrieval_handler = lambda_.Function(
            self, "VideoRetrievalHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="video_retrieval_handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambdas/api_handlers"),
            timeout=Duration.seconds(10),
            memory_size=256,
            role=lambda_role,
            environment={
                "FINAL_VIDEOS_TABLE": storage_stack.final_videos_table.table_name,
                "CONTENT_BUCKET": storage_stack.content_bucket.bucket_name
            }
        )
        
        # Grant additional table permissions
        storage_stack.translations_table.grant_read_write_data(lambda_role)
        storage_stack.scene_plans_table.grant_read_write_data(lambda_role)
        storage_stack.final_videos_table.grant_read_write_data(lambda_role)
        
        # Export Lambda ARNs for workflow stack
        cdk.CfnOutput(
            self, "TranscriptExtractorArn",
            value=self.transcript_extractor.function_arn,
            export_name="OrchestRAI-TranscriptExtractorArn"
        )
        cdk.CfnOutput(
            self, "ScriptGeneratorArn",
            value=self.script_generator.function_arn,
            export_name="OrchestRAI-ScriptGeneratorArn"
        )
        cdk.CfnOutput(
            self, "AICriticArn",
            value=self.ai_critic.function_arn,
            export_name="OrchestRAI-AICriticArn"
        )
        cdk.CfnOutput(
            self, "TranslationServiceArn",
            value=self.translation_service.function_arn,
            export_name="OrchestRAI-TranslationServiceArn"
        )
        cdk.CfnOutput(
            self, "ScenePlannerArn",
            value=self.scene_planner.function_arn,
            export_name="OrchestRAI-ScenePlannerArn"
        )
        cdk.CfnOutput(
            self, "VoiceSynthesizerArn",
            value=self.voice_synthesizer.function_arn,
            export_name="OrchestRAI-VoiceSynthesizerArn"
        )
        cdk.CfnOutput(
            self, "VideoAssemblerArn",
            value=self.video_assembler.function_arn,
            export_name="OrchestRAI-VideoAssemblerArn"
        )
        cdk.CfnOutput(
            self, "CompletionHandlerArn",
            value=self.completion_handler.function_arn,
            export_name="OrchestRAI-CompletionHandlerArn"
        )
        cdk.CfnOutput(
            self, "LambdaRoleArn",
            value=lambda_role.role_arn,
            export_name="OrchestRAI-LambdaRoleArn"
        )
        
        # TODO: Step Functions State Machine
        # Temporarily commented out to avoid circular dependency
        # Will be added in a future update
        
        # # Define states
        # extract_transcript = tasks.LambdaInvoke(
        #     self, "ExtractTranscript",
        #     lambda_function=transcript_extractor,
        #     output_path="$.Payload",
        #     retry_on_service_exceptions=True
        # )
        
        # # ... rest of Step Functions workflow ...
        
        # # Create state machine
        # self.state_machine = sfn.StateMachine(
        #     self, "VideoGenerationWorkflow",
        #     definition=definition,
        #     timeout=Duration.minutes(30),
        #     logs=sfn.LogOptions(
        #         destination=logs.LogGroup(self, "StateMachineLogs"),
        #         level=sfn.LogLevel.ALL
        #     )
        # )
        
        # Grant upload handler permission to start executions and store ARN
        # The workflow stack exports its ARN, so import it here via Fn.import_value.
        # This ensures the upload lambda can trigger Step Functions when invoked.
        # state machine ARN imported from workflow stack (Fn already imported globally)
        state_machine_arn = Fn.import_value("OrchestRAI-StateMachineArn")
        imported_sm = sfn.StateMachine.from_state_machine_arn(
            self, "ImportedWorkflow",
            state_machine_arn
        )

        # Grant the lambda permission to start executions on the imported state machine
        try:
            imported_sm.grant_start_execution(self.upload_handler)
        except Exception:
            pass

        # Ensure Lambda role has explicit permission to start executions (unconditional grant)
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["states:StartExecution"],
            resources=[state_machine_arn]
        ))

        # Provide the ARN to the handler via environment variable
        self.upload_handler.add_environment("STATE_MACHINE_ARN", state_machine_arn)

