#!/usr/bin/env python3
import aws_cdk as cdk

import add_tags
from cdk_compute.cdk_stack_api_lambda import CdkStackComputeApiLambda


DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "solar-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "solar-api"

app = cdk.App()

compute_stack = CdkStackComputeApiLambda(
    app,
    "{}-stack-compute-api-lambda-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)

add_tags.add_tags_to_stack(compute_stack)

app.synth()
