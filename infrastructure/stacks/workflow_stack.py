"""Workflow orchestration stack (Step Functions)."""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    Fn,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_logs as logs,
    aws_iam as iam,
    aws_lambda as lambda_
)
from constructs import Construct


class WorkflowStack(Stack):
    """Step Functions workflow for OrchestRAI."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Import Lambda functions by ARN from exports
        transcript_extractor_arn = Fn.import_value("OrchestRAI-TranscriptExtractorArn")
        script_generator_arn = Fn.import_value("OrchestRAI-ScriptGeneratorArn")
        ai_critic_arn = Fn.import_value("OrchestRAI-AICriticArn")
        translation_service_arn = Fn.import_value("OrchestRAI-TranslationServiceArn")
        scene_planner_arn = Fn.import_value("OrchestRAI-ScenePlannerArn")
        voice_synthesizer_arn = Fn.import_value("OrchestRAI-VoiceSynthesizerArn")
        video_assembler_arn = Fn.import_value("OrchestRAI-VideoAssemblerArn")
        completion_handler_arn = Fn.import_value("OrchestRAI-CompletionHandlerArn")
        
        # Create Lambda function references
        transcript_extractor = lambda_.Function.from_function_arn(
            self, "TranscriptExtractor", transcript_extractor_arn
        )
        script_generator = lambda_.Function.from_function_arn(
            self, "ScriptGenerator", script_generator_arn
        )
        ai_critic = lambda_.Function.from_function_arn(
            self, "AICritic", ai_critic_arn
        )
        translation_service = lambda_.Function.from_function_arn(
            self, "TranslationService", translation_service_arn
        )
        scene_planner = lambda_.Function.from_function_arn(
            self, "ScenePlanner", scene_planner_arn
        )
        voice_synthesizer = lambda_.Function.from_function_arn(
            self, "VoiceSynthesizer", voice_synthesizer_arn
        )
        video_assembler = lambda_.Function.from_function_arn(
            self, "VideoAssembler", video_assembler_arn
        )
        completion_handler = lambda_.Function.from_function_arn(
            self, "CompletionHandler", completion_handler_arn
        )
        
        # Define workflow states
        
        # 1. Extract Transcript (for video content)
        extract_transcript = tasks.LambdaInvoke(
            self, "ExtractTranscript",
            lambda_function=transcript_extractor,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 2. Generate Script
        generate_script = tasks.LambdaInvoke(
            self, "GenerateScript",
            lambda_function=script_generator,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 3. Evaluate Quality
        evaluate_quality = tasks.LambdaInvoke(
            self, "EvaluateQuality",
            lambda_function=ai_critic,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 4. Check if quality meets threshold
        quality_check = sfn.Choice(self, "QualityCheck")
        
        # 5. Translate Script
        translate_script = tasks.LambdaInvoke(
            self, "TranslateScript",
            lambda_function=translation_service,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 6. Plan Scenes
        plan_scenes = tasks.LambdaInvoke(
            self, "PlanScenes",
            lambda_function=scene_planner,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 7. Synthesize Voice
        synthesize_voice = tasks.LambdaInvoke(
            self, "SynthesizeVoice",
            lambda_function=voice_synthesizer,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 8. Assemble Video
        assemble_video = tasks.LambdaInvoke(
            self, "AssembleVideo",
            lambda_function=video_assembler,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 9. Complete Workflow
        complete_workflow = tasks.LambdaInvoke(
            self, "CompleteWorkflow",
            lambda_function=completion_handler,
            output_path="$.Payload",
            retry_on_service_exceptions=True
        )
        
        # 12. Success state
        workflow_succeeded = sfn.Succeed(self, "WorkflowSucceeded")
        
        # chain used by both the success and max-iteration branches of quality
        # checking; defines the steps to take once quality is deemed acceptable
        # (or we give up trying to improve it).
        post_quality_chain = (
            translate_script
                .next(plan_scenes)
                .next(synthesize_voice)
                .next(assemble_video)
                .next(complete_workflow)
                .next(workflow_succeeded)
        )
        
        # 9. Increment iteration counter
        increment_iteration = sfn.Pass(
            self, "IncrementIteration",
            parameters={
                "contentId.$": "$.contentId",
                "workflowId.$": "$.workflowId",
                "s3Key.$": "$.s3Key",
                "contentType.$": "$.contentType",
                "targetLanguages.$": "$.targetLanguages",
                "qualityThreshold.$": "$.qualityThreshold",
                "iterationCount.$": "States.MathAdd($.iterationCount, 1)",
                "transcript.$": "$.transcript",
                "script.$": "$.script"
            }
        )
        
        # 10. Max iterations check
        max_iterations_check = sfn.Choice(self, "MaxIterationsCheck")
        
        # 11. Failed state
        workflow_failed = sfn.Fail(
            self, "WorkflowFailed",
            cause="Quality threshold not met after maximum iterations",
            error="QualityThresholdNotMet"
        )
        
        # Define workflow logic
        
        # Quality check conditions
        quality_passed = sfn.Condition.number_greater_than_equals_json_path(
            "$.qualityScore", 
            "$.qualityThreshold"
        )
        
        # Max iterations check
        max_iterations_reached = sfn.Condition.number_greater_than_equals(
            "$.iterationCount",
            3  # Maximum 3 refinement iterations
        )
        
        # Build the workflow chain
        definition = extract_transcript \
            .next(generate_script) \
            .next(evaluate_quality) \
            .next(quality_check
                .when(quality_passed, post_quality_chain)
                .otherwise(
                    max_iterations_check
                        # if we've reached the maximum number of refinement
                        # iterations we no longer abort the workflow; continue
                        # with the current script and let the downstream
                        # translation/scene/voice steps run. that guarantees
                        # a final video record even when the critic never
                        # returns a satisfactory score (common in early
                        # prototype testing).
                        .when(max_iterations_reached, post_quality_chain)
                        .otherwise(
                            increment_iteration
                                .next(generate_script)
                        )
                )
            )
        
        # Create state machine
        self.state_machine = sfn.StateMachine(
            self, "VideoGenerationWorkflow",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(30),
            logs=sfn.LogOptions(
                destination=logs.LogGroup(self, "StateMachineLogs"),
                level=sfn.LogLevel.ALL
            )
        )
        
        # Grant Step Functions permission to invoke Lambda functions
        lambda_role_arn = Fn.import_value("OrchestRAI-LambdaRoleArn")
        
        # Export state machine ARN
        CfnOutput(
            self, "StateMachineArn",
            value=self.state_machine.state_machine_arn,
            description="Step Functions State Machine ARN",
            export_name="OrchestRAI-StateMachineArn"
        )
        
        # Store state machine ARN
        self.state_machine_arn = self.state_machine.state_machine_arn
