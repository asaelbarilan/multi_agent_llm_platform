# agents/utils.py

import os
import re
import json

def extract_application_name(my_string):
    """
    Extracts the application name from a given string in various formats.
    """
    # Updated regex pattern to handle different formats
    pattern = r'^\s*(?:#|\*\*)\s*(?:Application Name:\s*)?([A-Za-z0-9_ ]+)'

    match = re.search(pattern, my_string, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return None

def parse_files_from_response(response):
    try:
        # Attempt to find the JSON object in the response
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            print("Extracted JSON content:", json_content)  # Debugging line

            # Attempt to parse the JSON content
            data = json.loads(json_content)
            app_name = data.get("application_name", None)
            files = {file["path"]: file["content"] for file in data.get("files", [])}
            return files, app_name
        else:
            print("No JSON content found in the agent's response.")
            return {}, None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")

        # Attempt to fix common issues
        try:
            # Remove triple quotes
            json_content = response.replace('"""', '"')
            print("Removed triple quotes from response.")  # Debugging line

            # Escape unescaped double quotes within strings
            json_content = re.sub(r'(?<!\\)"', r'\\"', json_content)
            print("Escaped double quotes.")  # Debugging line

            # Replace single quotes with double quotes
            json_content = json_content.replace("'", '"')
            print("Replaced single quotes with double quotes.")  # Debugging line

            # Parse the cleaned JSON content
            data = json.loads(json_content)
            app_name = data.get("application_name", None)
            files = {file["path"]: file["content"] for file in data.get("files", [])}
            return files, app_name
        except json.JSONDecodeError as e2:
            print(f"JSON parsing error after attempting to fix: {e2}")
            return {}, None

def create_unique_folder(folder_name):
    if folder_name is None:
        folder_name='NewApp'
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# agents/utils.py

import json
import re

# Existing imports and functions...

def validate_agent_response(response, required_fields):
    """
    Validates the agent's response to ensure it is valid JSON and contains required fields.
    Returns a tuple (is_valid, data_or_error_message).
    """
    try:
        # Attempt to find the JSON object in the response
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            data = json.loads(json_content)
            # Check for required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            return True, data
        else:
            return False, "No valid JSON content found in the response."
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
