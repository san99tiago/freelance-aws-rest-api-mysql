#!/usr/bin/env python3
import aws_cdk as cdk

# Build-in imports
import os
import datetime

# Get deployment environment from env variable or default to development
environment = os.getenv("ENVIRONMENT", "dev").lower()

DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = environment
NAME_PREFIX = "{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "solar-api"
AUTHORS = "Santiago Garcia Arango"


def add_tags_to_stack(stack):
    """
    Simple function to add custom tags to stack in a centralized (equal) approach.
    """

    # Obtain current datetime for timestamp record
    now = datetime.datetime.now()
    datetime_formatted = now.strftime("%Y-%m-%d")

    cdk.Tags.of(stack).add("Environment", DEPLOYMENT_ENVIRONMENT)
    cdk.Tags.of(stack).add("Authors", AUTHORS)
    cdk.Tags.of(stack).add("Identifier", MAIN_RESOURCES_NAME)
    cdk.Tags.of(stack).add("LastDeploymentDate", datetime_formatted)


def validate_correct_deployment_environment(environment):
    """
    Simple function that validates the deployment environment.
    """
    if environment == "dev" or environment == "prod":
        print("Environment for deployment is: {}".format(environment))
        return True
    else:
        print("THE ENVIRONMENT FOR THE DEPLOYMENT IS NOT VALID (ONLY ALLOWED \"DEV\" or \"PROD\")")
        return False
