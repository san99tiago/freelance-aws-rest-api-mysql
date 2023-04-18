# API RETURN FORMAT FOR LAMBDA FUNCTIONS (BASED ON API-GATEWAY STANDARDS)


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
