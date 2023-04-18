#!/usr/bin/env python3
import os
import aws_cdk as cdk

import global_configurations as global_configs
from cdk_storage.cdk_stack_rds import CdkStackStorageRDS


# Validate deployment pre-requisites
valid_deployment = global_configs.validate_correct_deployment_environment(global_configs.DEPLOYMENT_ENVIRONMENT)
if valid_deployment == False:
    raise Exception({"SolarApiError": "Environment '{}' is not valid. Use 'dev' or 'prod'.".format(global_configs.DEPLOYMENT_ENVIRONMENT)})

# Configure variables based on deployment environment
if global_configs.DEPLOYMENT_ENVIRONMENT == "dev":
    instance_type_class = cdk.aws_ec2.InstanceClass.BURSTABLE4_GRAVITON
    instance_type_size = cdk.aws_ec2.InstanceSize.SMALL
    deletion_protection = False
    removal_policy = cdk.RemovalPolicy.DESTROY
    multi_az = False
    delete_automated_backups = True
    backup_retention = cdk.Duration.days(0)
    custom_database_name = "solar_db"
    enable_performance_insights = False
elif global_configs.DEPLOYMENT_ENVIRONMENT == "prod":
    instance_type_class = cdk.aws_ec2.InstanceClass.BURSTABLE4_GRAVITON
    instance_type_size = cdk.aws_ec2.InstanceSize.LARGE
    deletion_protection = True
    removal_policy = cdk.RemovalPolicy.RETAIN
    multi_az = True
    delete_automated_backups = False
    backup_retention = cdk.Duration.days(2)
    custom_database_name = "solar_db"
    enable_performance_insights = True

app = cdk.App()
storage_stack = CdkStackStorageRDS(
    app,
    "{}-{}-stack-storage-rds-cdk".format(global_configs.DEPLOYMENT_ENVIRONMENT, global_configs.MAIN_RESOURCES_NAME),
    global_configs.NAME_PREFIX,
    global_configs.MAIN_RESOURCES_NAME,
    global_configs.DEPLOYMENT_ENVIRONMENT,
    global_configs.DEPLOYMENT_VERSION,
    instance_type_class,
    instance_type_size,
    deletion_protection,
    removal_policy,
    multi_az,
    delete_automated_backups,
    backup_retention,
    custom_database_name,
    enable_performance_insights,
    env={
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
        "region": os.environ["CDK_DEFAULT_REGION"]
    },
    description="Stack for Storage (RDS) for {} solution in {} environment".format(global_configs.MAIN_RESOURCES_NAME, global_configs.DEPLOYMENT_ENVIRONMENT),
)
global_configs.add_tags_to_stack(storage_stack)
app.synth()
