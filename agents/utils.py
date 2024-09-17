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
    # Extract JSON content from the response
    try:
        # Attempt to find the JSON object in the response
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)

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

            # Escape unescaped double quotes within strings
            json_content = re.sub(r'(?<!\\)"', r'\\"', json_content)

            # Replace single quotes with double quotes
            json_content = json_content.replace("'", '"')

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

