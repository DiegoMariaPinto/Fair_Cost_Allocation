import re
import os
##################################################################################################
def find_file_with_texts(folder_path, text1, text2):
    # Compile a regex pattern with the two texts
    pattern = re.compile(f".*{re.escape(text1)}.*{re.escape(text2)}.*")
    # List all files in the specified folder
    files = os.listdir(folder_path)
    # Iterate through the files and find the one that matches the pattern
    for file_name in files:
        if pattern.match(file_name):
            return file_name
    # Return None if no matching file is found
    return None

def extract_substring(input_string, start_string, end_string):
    # Construct a regex pattern to match the substring between start and end strings
    pattern = re.compile(f'{re.escape(start_string)}(.*?){re.escape(end_string)}')
    # Search for the pattern in the input string
    match = pattern.search(input_string)
    # Return the matched substring if found, or None if not found
    return match.group(1) if match else None
##################################################################################################