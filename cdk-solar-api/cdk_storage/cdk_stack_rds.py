import os

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_dynamodb,
    RemovalPolicy,
)
from constructs import Construct

class CdkStackStorageRDS(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name_prefix: str,
        main_resources_name: str,
        deployment_environment: str,
        deployment_version: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.main_resources_name = main_resources_name
        self.deployment_environment = deployment_environment
        self.deployment_version = deployment_version

        # DynamoDB creation
        self.create_rds()

        # Relevant CloudFormation outputs
        self.show_cloudformation_outputs()

    # TODO: Validate if RDS secret should be here or not

    def create_rds(self):
        """
        Method to create the RDS for MySQL.
        """
        # TODO
        pass


    def show_cloudformation_outputs(self):
        """
        Method to create/add the relevant CloudFormation outputs.
        """
        CfnOutput(
            self,
            "DeploymentVersion",
            value=self.deployment_version,
            description="Current deployment's version",
        )

        CfnOutput(
            self,
            "DeploymentEnvironment",
            value=self.deployment_environment,
            description="Deployment environment",
        )

        CfnOutput(
            self,
            "NamePrefixes",
            value=self.name_prefix,
            description="Name prefixes for the resources",
        )
