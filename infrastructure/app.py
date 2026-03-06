#!/usr/bin/env python3
"""AWS CDK app for OrchestRAI infrastructure."""
import aws_cdk as cdk
from stacks.storage_stack import StorageStack
from stacks.compute_stack import ComputeStack
from stacks.api_stack import ApiStack
from stacks.workflow_stack import WorkflowStack


app = cdk.App()

# Define environment (explicitly set to us-east-1)
# Replace with your AWS account ID
env = cdk.Environment(account="YOUR_AWS_ACCOUNT_ID", region="us-east-1")

# Storage layer (S3 + DynamoDB)
storage_stack = StorageStack(
    app, "OrchestRAIStorageStack",
    env=env,
    description="Storage infrastructure for OrchestRAI"
)

# Compute layer (Lambda functions)
compute_stack = ComputeStack(
    app, "OrchestRAIComputeStack",
    env=env,
    storage_stack=storage_stack,
    description="Compute infrastructure for OrchestRAI"
)

# Workflow layer (Step Functions) - deployed separately after Compute Stack
workflow_stack = WorkflowStack(
    app, "OrchestRAIWorkflowStack",
    env=env,
    description="Workflow orchestration for OrchestRAI"
)
workflow_stack.add_dependency(compute_stack)

# API layer (API Gateway)
api_stack = ApiStack(
    app, "OrchestRAIApiStack",
    env=env,
    compute_stack=compute_stack,
    description="API infrastructure for OrchestRAI"
)

app.synth()
