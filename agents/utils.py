# agents/utils.py

import os
import re

def extract_application_name(my_string):
    """
    Extracts the application name from a given string in various formats.

    Args:
        my_string (str): The input string containing the application name.

    Returns:
        str or None: The extracted application name if found, else None.
    """
    # Updated regex pattern to handle different formats
    pattern = r'^(?:\#|\*\*)Application Name:\**\s*([A-Za-z0-9_]+)'

    # Use re.MULTILINE to handle strings with multiple lines
    match = re.search(pattern, my_string, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None

def parse_files_from_response(response):
    files = {}
    app_name = extract_application_name(response)  # Use the updated extraction function

    # Define forbidden characters excluding '/'
    forbidden_chars = r'<>:"\\|?*'

    # Patterns to match the expected file format with '# File: filename' or '**File: filename**'
    pattern1 = r'# File:\s*(.*?)\s*\n```(?:\w+)?\n([\s\S]*?)\n```'
    pattern2 = r'\*\*File:\s*(.*?)\*\*\n```(?:\w+)?\n([\s\S]*?)\n```'

    # Find all matches for pattern1
    matches1 = re.finditer(pattern1, response, re.DOTALL)
    for match in matches1:
        file_path = match.group(1).strip()
        code = match.group(2).strip()

        # Sanitize the file path (allow forward slashes)
        if any(c in file_path for c in forbidden_chars):
            print(f"Invalid characters found in file path: {file_path}. Skipping this file.")
            continue

        files[file_path] = code

    # Find all matches for pattern2
    matches2 = re.finditer(pattern2, response, re.DOTALL)
    for match in matches2:
        file_path = match.group(1).strip()
        code = match.group(2).strip()

        # Sanitize the file path (allow forward slashes)
        if any(c in file_path for c in forbidden_chars):
            print(f"Invalid characters found in file path: {file_path}. Skipping this file.")
            continue

        files[file_path] = code

    if not files:
        print("No valid code files found in the agent's response.")

    return files, app_name


def create_unique_folder(folder_name):
    if folder_name is None:
        folder_name='NewApp'
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

