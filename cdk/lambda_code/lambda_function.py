# Built-in imports
import logging
import os
import json
import boto3

# Own imports
import api_return_format
import rds_helpers
import input_validations

# External dependencies imports (from lambda layer)
from aws_lambda_powertools.utilities import parameters
import mysql.connector


# Configure logging
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# Get environment variables for RDS and Secrets
TABLE_NAME = os.environ.get("TABLE_NAME")
RDS_HOST = os.environ.get("RDS_HOST")
RDS_DATABASE = os.environ.get("RDS_DATABASE")
RDS_SECRET_NAME = os.environ.get("RDS_SECRET_NAME")
API_SECRET_NAME = os.environ.get("API_SECRET_NAME")

# Fetch secrets from AWS Secrets
rds_secret = json.loads(parameters.get_secret(RDS_SECRET_NAME))
api_secret = json.loads(parameters.get_secret(API_SECRET_NAME))


# Load RDS connector
mydb_connector = mysql.connector.connect(
    host=RDS_HOST,
    user=rds_secret["username"],
    password=rds_secret["password"],
    database=RDS_DATABASE,
)


def lambda_handler(event, context):
    """
    Lambda function handler for the overall functionality orchestration.
    """

    LOG.info("lambda_handler: event is {}".format(event))

    # Obtain source IP address (X-Forwarded-For header) for client's info
    x_forwarded_for_values = event["headers"]["X-Forwarded-For"]
    print("header <x_forwarded_for_values> is: {}".format(x_forwarded_for_values))
    x_forwarded_for_source_ip = x_forwarded_for_values.split(",")[0]
    x_forwarded_for_aws_ip = x_forwarded_for_values.split(",")[1]

    # Default ids
    agent_id = None
    lead_id = None
    supplier_id = None

    # Validations of the API call and query-parameters
    if event["queryStringParameters"] is not None:
        # Validation of query params
        username_validation = "username" in event["queryStringParameters"]
        password_validation = "password" in event["queryStringParameters"]
        lead_id_validation = "lead_id" in event["queryStringParameters"]
        supplier_id_validation = "supplier_id" in event["queryStringParameters"]
        agent_id_validation = "agent_id" in event["queryStringParameters"]

        # Add missing query parameters for internal logging purposes (records_table)
        missing_query_params = []
        if username_validation == False:
            missing_query_params.append("username")
        if password_validation == False:
            missing_query_params.append("password")
        if lead_id_validation == False:
            missing_query_params.append("lead_id")
        if supplier_id_validation == False:
            missing_query_params.append("supplier_id")
        if agent_id_validation == False:
            missing_query_params.append("agent_id")

        # Validate non-missing params
        if len(missing_query_params) == 0:
            agent_id = event["queryStringParameters"]["agent_id"]
            supplier_id = event["queryStringParameters"]["supplier_id"]
            lead_id = event["queryStringParameters"]["lead_id"]
            api_username = event["queryStringParameters"]["username"]
            api_password = event["queryStringParameters"]["password"]

            # Add empty_input_params validations
            empty_input_params = []
            if input_validations.is_empty_input(agent_id) == True:
                empty_input_params.append("agent_id")
            if input_validations.is_empty_input(supplier_id) == True:
                empty_input_params.append("supplier_id")
            if input_validations.is_empty_input(lead_id) == True:
                empty_input_params.append("lead_id")
            if input_validations.is_empty_input(api_username) == True:
                empty_input_params.append("username")
            if input_validations.is_empty_input(api_password) == True:
                empty_input_params.append("password")

            # Only continue workflow if all parameters are non-empty
            if len(empty_input_params) == 0:
                # Authentication for Solar API (retrieved from secret)
                if api_secret["username"] == api_username and api_secret["password"] == api_password:
                    api_final_result =  rds_helpers.read_lead_from_id(mydb_connector, lead_id)
                    print("api_final_result status code is : {}".format(api_final_result["statusCode"]) )

                    if api_final_result["statusCode"] == 200:
                        # Add logs of successful request details to rds records table
                        rds_insert_request_response = rds_helpers.create_update_api_request_summary(
                            mydb_connector,
                            agent_id,
                            lead_id,
                            supplier_id,
                            "successful",
                            None,
                            x_forwarded_for_source_ip,
                            x_forwarded_for_aws_ip,
                        )
                        print("rds_insert_request_response for request info is : {}".format(rds_insert_request_response))
                        return api_final_result
                    else:
                        # Response when it has a non-existent lead_id
                        record_error_message = "Wrong lead_id {}".format(api_final_result["body"])
                else:
                    # Response when there is an error on the username and/or password
                    record_error_message = "Wrong username and/or password"
            else:
                # Response when there are empty input_parameters (ex: " " or "  " or blank-spaces)
                record_error_message = "Request had the following empty query parameters {}".format(empty_input_params)
        else:
            # Response when there is a missing query parameter on the request
            record_error_message = "Request did not contain the following query parameters {}".format(missing_query_params)
    else:
        # Response when there are no query parameters at all (all missing)
        record_error_message = "Request did not contain ANY query parameters (all were missing)"

    # Add logs of failure request details to rds records table
    rds_insert_request_response = rds_helpers.create_update_api_request_summary(
        mydb_connector,
        agent_id,
        lead_id,
        supplier_id,
        "failure",
        record_error_message,
        x_forwarded_for_source_ip,
        x_forwarded_for_aws_ip,
    )
    print("rds_insert_request_response for request info is : {}".format(rds_insert_request_response))

    # If a validation fails, return usage explanation message (how to call API)
    return_usage_dict = {
        "instructions": "Please call this endpoint as the <usage> indicates...",
        "usage": "?username=username&password=password&supplier_id=supplier_id&agent_id=agent_id&lead_id=lead_id",
    }
    return api_return_format.get_return_format(200, json.dumps(return_usage_dict, indent=2, default=str))
