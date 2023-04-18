import os
import json

from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_secretsmanager,
    aws_rds,
    aws_ec2,
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
        instance_type_class: aws_ec2.InstanceClass,
        instance_type_size: aws_ec2.InstanceSize,
        deletion_protection: bool,
        removal_policy: RemovalPolicy,
        multi_az: bool,
        delete_automated_backups: bool,
        backup_retention: Duration,
        custom_database_name: str,
        enable_performance_insights: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load parameters to class attributes
        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.main_resources_name = main_resources_name
        self.deployment_environment = deployment_environment
        self.deployment_version = deployment_version
        self.instance_type_class = instance_type_class
        self.instance_type_size = instance_type_size
        self.deletion_protection = deletion_protection
        self.removal_policy = removal_policy
        self.multi_az = multi_az
        self.delete_automated_backups = delete_automated_backups
        self.backup_retention = backup_retention
        self.enable_performance_insights = enable_performance_insights

        # Name of the database
        self.custom_database_name = custom_database_name

        # Secrets Manager Secret creation
        self.create_secret_for_api_authentication()
        self.create_secret_for_rds_credentials()

        # RDS creation
        self.get_default_vpc()
        self.create_security_group_for_rds()
        self.create_rds()

        # Relevant CloudFormation outputs
        self.show_cloudformation_outputs()


    def create_secret_for_api_authentication(self):
        """
        Method to create an AWS Secrets Manager Secret for API authentication.
        """
        # Create secret with auto-generated password (for DB security credentials)
        self.api_secret = aws_secretsmanager.Secret(
            self,
            id="{}-SecretAPICredentials".format(self.construct_id),
            secret_name="{}{}-SecretAPICredentials".format(self.name_prefix, self.main_resources_name),
            description="Secret for the RDS of the {} stack in ({}) environment".format(self.main_resources_name, self.deployment_environment),
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps(
                    {
                        "username": "solar",
                    }
                ),
                generate_string_key="password",
                exclude_characters="/@'\" .%;?:&=+$,<>}{!`[]|-\\*)(#^~"
            )
        )

    def create_secret_for_rds_credentials(self):
        """
        Method to create an AWS Secrets Manager Secret for RDS credentials.
        """
        # Create secret with auto-generated password (for DB security credentials)
        self.database_secret = aws_secretsmanager.Secret(
            self,
            id="{}-SecretRDSCredentials".format(self.construct_id),
            secret_name="{}{}-SecretRDSCredentials".format(self.name_prefix, self.main_resources_name),
            description="Secret for the RDS of the {} stack in ({}) environment".format(self.main_resources_name, self.deployment_environment),
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps(
                    {
                        "username": "admin",
                    }
                ),
                generate_string_key="password",
                exclude_characters="/@'\" "
            )
        )


    def get_default_vpc(self):
        """
        Method to get the default VPC for the networking configurations.
        """
        # Retrieve default  VPC information
        self.default_vpc = aws_ec2.Vpc.from_lookup(
            self,
            id="{}-VPC".format(self.construct_id),
            is_default=True,
        )


    def create_security_group_for_rds(self):
        """
        Method to create the security group for RDS access.
        """
        self.db_security_group = aws_ec2.SecurityGroup(
            self,
            id="{}-SG".format(self.construct_id),
            description="SG for access to RDS of {} solution in ({}) environment".format(self.main_resources_name, self.deployment_environment),
            allow_all_outbound=True,
            vpc=self.default_vpc,
        )

        self.db_security_group.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(3306),
            description="Allow connections for port database port",
        )


    def create_rds(self):
        """
        Method to create the RDS for MySQL.
        """
        self.db_instance = aws_rds.DatabaseInstance(
            self,
            id="{}-RDS".format(self.construct_id),
            database_name=self.custom_database_name,
            engine=aws_rds.DatabaseInstanceEngine.MYSQL,
            credentials=aws_rds.Credentials.from_secret(self.database_secret),
            deletion_protection=self.deletion_protection,
            removal_policy=self.removal_policy,
            instance_type=aws_ec2.InstanceType.of(self.instance_type_class, self.instance_type_size),
            instance_identifier="{}-{}".format(self.deployment_environment, self.main_resources_name),
            multi_az=self.multi_az,
            publicly_accessible=True,
            security_groups=[self.db_security_group],
            vpc=self.default_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PUBLIC
            ),
            iam_authentication=False,
            delete_automated_backups=self.delete_automated_backups,
            auto_minor_version_upgrade=True,
            backup_retention=self.backup_retention,
            enable_performance_insights=self.enable_performance_insights
        )


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

        CfnOutput(
            self,
            "APICredentialsSecretName",
            value=self.api_secret.secret_name,
            description="Name of the AWS Secret for the APICredentials credentials",
            export_name="SecretNameForAPICredentials{}".format(self.deployment_environment)
        )

        CfnOutput(
            self,
            "APICredentialsSecretFullARN",
            value=self.api_secret.secret_full_arn,
            description="Full ARN of the AWS Secret for the API credentials",
        )

        CfnOutput(
            self,
            "RDSSecretName",
            value=self.database_secret.secret_name,
            description="Name of the AWS Secret for the RDS credentials",
            export_name="SecretNameForRDSCredentials{}".format(self.deployment_environment)
        )

        CfnOutput(
            self,
            "RDSSecretFullARN",
            value=self.database_secret.secret_full_arn,
            description="Full ARN of the AWS Secret for the RDS credentials",
        )

        CfnOutput(
            self,
            "RDSPort",
            value=self.db_instance.db_instance_endpoint_port,
            description="Port of the RDS",
        )

        CfnOutput(
            self,
            "RDSHost",
            value=self.db_instance.db_instance_endpoint_address,
            description="Host of the RDS (endpoint)",
            export_name="RDSHost{}".format(self.deployment_environment)
        )

        CfnOutput(
            self,
            "RDSDBName",
            value=self.custom_database_name,
            description="Name of the database on the RDS",
            export_name="RDSDBName{}".format(self.deployment_environment)
        )
