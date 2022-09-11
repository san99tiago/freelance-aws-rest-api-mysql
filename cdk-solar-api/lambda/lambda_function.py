import logging
import os
import json
import boto3

# Configure logging
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# Configure AWS resources
TABLE_NAME = os.environ.get("TABLE_NAME")
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(TABLE_NAME)


def read_lead(event):
    # TODO
    pass


def create_lead(event):
    # TODO
    pass


def lambda_handler(event, context):
    LOG.info("lambda_handler: event is {}".format(event))

    if event["queryStringParameters"] is not None:
        if event["queryStringParameters"]["username"] is not None:
            # TODO: add extra validations (pass, password, supplierID, leadID, agent_id, etc...)
            return read_lead(event)

    # TODO: Clarify "create_lead" functionality

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "instructions": "Please call this endpoint as the <type_usage> indicates...",
                "read_usage": "?username=XXXXX&password=XXXXX&supplierID=XXXXX&leadID=XXXXX&agent_id=XXXXX",
            }
            , sort_keys=True, default=str)
    }
