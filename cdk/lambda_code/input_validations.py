# API VALIDATORS FOR LAMBDA FUNCTIONS (BASED ON INPUT STANDARDS)


def is_empty_input(string_to_validate):
    """
    Function to validate input strings to disable empty string parameters on API.
    """
    trimmed_string = string_to_validate.strip()
    if trimmed_string == "":
        return True
    return False
