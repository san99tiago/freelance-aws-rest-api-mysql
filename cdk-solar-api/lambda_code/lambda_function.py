# Built-in imports
import logging
import os
import json
import boto3

# External dependencies imports (from lambda layer)
from aws_lambda_powertools.utilities import parameters
import mysql.connector

# Configure logging
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# Get environment variables for DynamoDB, RDS and Secrets
TABLE_NAME = os.environ.get("TABLE_NAME")
RDS_HOST = os.environ.get("RDS_HOST")
RDS_DATABASE = os.environ.get("RDS_DATABASE")
SECRET_NAME = os.environ.get("SECRET_NAME")

# Configure AWS resources
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(TABLE_NAME)
rds_secret = parameters.get_secret(SECRET_NAME)

# Load RDS connector
mydb = mysql.connector.connect(
    host=RDS_HOST,
    user=rds_secret["username"],
    password=rds_secret["password"],
    database=RDS_DATABASE,
)



def get_return_format(status_code, body):
    """
    Function that returns the required response for the lambda function.
    :param status_code: int --> status code for the REST API response (Ex: 200, 400, ...).
    :param body: string --> Response body for the REST API (Ex: "Missing body parameter").
    """
    return {
        "statusCode": status_code,
        "body": body
    }


def read_lead_from_id(event, lead_id):
    """
    Function to read a lead row from lead_id information.
    :param lead_id: identifier for the lead (str)
    :return: lead_id_json structure with result (JSON) or None.
    """
    try:
        # Create cursor for DB functionality
        cursor = mydb.cursor()
    
        # Execute main query for leads
        cursor.execute("SELECT * FROM solar_db.leads_table WHERE lead_id='{}'".format(lead_id))
        
        # Get one result (as there are never lead_id duplicates)
        query_result = cursor.fetchone()
        print("query_result is :", query_result)
        
        # Validate query response to be not None (that lead_id exists)
        if query_result is not None:
            col_names = cursor.column_names
            json_response = {}
            for i in range(len(col_names)):
                json_response[col_names[i]] = query_result[i]
        else:
            json_response = {
                "message": "There was not a match for the query.",
                "details": "Server unable to read request"}
        print("json_response is: ", json_response)

        cursor.close()
        mydb.close()

        return get_return_format(200, json.dumps(json_response, indent=2, default=str))
    except mysql.connector.Error as e:
        print("Error reading data from MySQL table: ", e)


def create_lead(event):
    # TODO: for future development when leads_are going to be created through API calls
    pass


def lambda_handler(event, context):
    """
    Lambda function handler for the overall functionality orchestration.
    """

    LOG.info("lambda_handler: event is {}".format(event))
    
    # Validations of the API call and query-parameters
    if event["queryStringParameters"] is not None:
        # Validation of query params
        username_validation = "username" in event["queryStringParameters"]
        password_validation = "password" in event["queryStringParameters"]
        lead_id_validation = "lead_id" in event["queryStringParameters"]
        supplier_id_validation = "supplier_id" in event["queryStringParameters"]
        agent_id_validation = "agent_id" in event["queryStringParameters"]

        if (username_validation and password_validation and lead_id_validation and supplier_id_validation and agent_id_validation):
            lead_id = event["queryStringParameters"]["lead_id"]
            # TODO: add validation to lead_id constraints!!!

            return read_lead_from_id(event, lead_id)


    # If a validation fails, return usage explanation message (how to call API)
    return_usage_dict = {
                "instructions": "Please call this endpoint as the <type_usage> indicates...",
                "read_usage": "?username=<username>&password=<password>&supplier_id=<supplier_id>&lead_id=<lead_id>&agent_id=<agent_id>",
    }
    return get_return_format(200, return_usage_dict)
