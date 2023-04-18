#!/usr/bin/env python3
import os
import aws_cdk as cdk

import global_configurations as global_configs
from cdk_compute.cdk_stack_api_lambda import CdkStackComputeApiLambda

# Validate deployment pre-requisites
valid_deployment = global_configs.validate_correct_deployment_environment(global_configs.DEPLOYMENT_ENVIRONMENT)
if valid_deployment == False:
    raise Exception({"SolarApiError": "Environment '{}' is not valid. Use 'dev' or 'prod'.".format(global_configs.DEPLOYMENT_ENVIRONMENT)})

app = cdk.App()
compute_stack = CdkStackComputeApiLambda(
    app,
    "{}-{}-stack-compute-api-lambda-cdk".format(global_configs.DEPLOYMENT_ENVIRONMENT, global_configs.MAIN_RESOURCES_NAME),
    global_configs.NAME_PREFIX,
    global_configs.MAIN_RESOURCES_NAME,
    global_configs.DEPLOYMENT_ENVIRONMENT,
    global_configs.DEPLOYMENT_VERSION,
    env={
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
        "region": os.environ["CDK_DEFAULT_REGION"]
    },
    description="Stack for Compute (API, Lambda) for {} solution in {} environment".format(global_configs.MAIN_RESOURCES_NAME, global_configs.DEPLOYMENT_ENVIRONMENT),
)
global_configs.add_tags_to_stack(compute_stack)
app.synth()
