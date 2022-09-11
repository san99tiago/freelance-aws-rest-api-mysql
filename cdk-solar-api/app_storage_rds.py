#!/usr/bin/env python3
import aws_cdk as cdk

import add_tags
from cdk_storage.cdk_stack_rds import CdkStackStorageRDS


DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "solar-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "solar-api"

app = cdk.App()

storage_stack = CdkStackStorageRDS(
    app,
    "{}-stack-storage-rds-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)

add_tags.add_tags_to_stack(storage_stack)

app.synth()
