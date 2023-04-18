# HELPERS FOR RDS QUERIES

# Built-in imports
import json
import datetime

# Own imports
import api_return_format

# External dependencies imports (from lambda layer)
import mysql.connector


def read_lead_from_id(mysql_connector, lead_id):
    """
    Function to read a lead row from lead_id information.
    :param mysql_connector: mysql-connector for RDS queries.
    :param lead_id: identifier for the lead (str).
    :return: lead_id_json structure with result (JSON) or None.
    """
    try:
        # Create cursor for DB functionality
        cursor = mysql_connector.cursor()

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
            status_code_response = 200
        else:
            json_response = {
                "message": "There was not a match for the query.",
                "details": "Server unable to get request due to wrong query (lead_id)."}
            status_code_response = 400
        print("json_response is: ", json_response)

        return api_return_format.get_return_format(status_code_response, json.dumps(json_response, indent=2, default=str))
    except mysql.connector.Error as e:
        error_message = "Error reading data from MySQL table: ", e
        print(error_message)
        return api_return_format.get_return_format(400, json.dumps(error_message, indent=2, default=str))


def create_update_api_request_summary(mysql_connector, agent_id, lead_id, supplier_id, result, extra_information, source_ip, internal_aws_ip):
    """
    Function to create an API request information summary to the records table (logs at API).
    :param mysql_connector: mysql-connector for RDS queries.
    :param agent_id: agent id (string).
    :param lead_id: lead id (string).
    :param supplier_id: supplier id (string).
    :param result: result of RDS query (string).
    :param extra_information: reason for failure (string).
    :param source_ip: IP address of client (string).
    :param internal_aws_ip: IP address of client (string).
    """
    # Obtain current datetime for timestamp record
    now = datetime.datetime.now()
    datetime_formatted = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        # Create cursor for DB functionality
        cursor = mysql_connector.cursor()

        # Create query structures for inserting API requests to the records table
        add_record_query_template = ("INSERT INTO `solar_db`.`api_records_table` "
                    "(`request_date_time`, `lead_id`, `agent_id`, `supplier_id`, `result`, `extra_information`, `source_ip`, `internal_aws_ip`) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

        record_data_to_add = (
            datetime_formatted,
            lead_id,
            agent_id,
            supplier_id,
            result,
            extra_information,
            source_ip,
            internal_aws_ip
        )

        # Insert the request based on given information
        cursor.execute(add_record_query_template, record_data_to_add)

        # Make sure data is committed to the database
        mysql_connector.commit()

        last_row_id = cursor.lastrowid
        print("Row added to api_records_table row inserted: ", last_row_id)

        return last_row_id

    except mysql.connector.Error as e:
        error_message = "Error adding the API request to the records table: ", e
        print(error_message)
        return error_message


# --------- LOCAL TESTS ONLY ---------
if __name__ == "__main__":
    import os
    # Load RDS connector information (must be in environment variables)
    print(os.getenv("RDS_HOST"))
    print(os.getenv("RDS_USER"))
    print(os.getenv("RDS_PASSWORD"))
    print(os.getenv("RDS_DATABASE"))

    mydb_connector = mysql.connector.connect(
        host=os.getenv("RDS_HOST"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD"),
        database=os.getenv("RDS_DATABASE"),
    )

    # Reads lead information example 1 (Found)
    api_final_result =  read_lead_from_id(mydb_connector, "1234567890")
    print("api_final_result status code is : {}".format(api_final_result["statusCode"]) )

    # Reads lead information example 2 (Not found)
    api_final_result =  read_lead_from_id(mydb_connector, "0000000000")
    print("api_final_result status code is : {}".format(api_final_result["statusCode"]) )

    # Add logs of failure request details to rds records table
    rds_insert_request_response = create_update_api_request_summary(
        mydb_connector,
        "12345",
        "11111",
        None,
        "failure",
        "The request to the endpoint did not contain all the necessary correct query parameters.",
        "1.2.3.4",
        "5.6.7.8"
    )
    print("rds_insert_request_response for request info is : {}".format(rds_insert_request_response))
