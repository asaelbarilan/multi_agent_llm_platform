import os

def folder_to_text_file(folder_path, output_file="output.txt"):
    with open(output_file, "w") as f_out:
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                f_out.write(f"File: {file}\nPath: {file_path}\n\n")
                # Read the content of each file and write to output file
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                        content = f_in.read()
                        f_out.write(content)
                        f_out.write("\n\n" + "="*50 + "\n\n")
                except Exception as e:
                    f_out.write(f"Error reading file {file}: {str(e)}\n\n" + "="*50 + "\n\n")
    print(f"All files from {folder_path} have been written to {output_file}.")


def folder_to_text_file_big(folder_path, output_folder="multi_agent_llm_platform", max_file_size_mb=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_index = 1
    output_file = os.path.join(output_folder, f"output_{output_index}.txt")
    f_out = open(output_file, "w")
    current_size = 0
    max_size_bytes = max_file_size_mb * 1024 * 1024  # Convert MB to bytes

    # Walk through the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    content = f_in.read()

                    # Check the size of the current file to be written
                    file_size = len(content.encode('utf-8'))
                    file_header = f"File: {file}\nPath: {file_path}\n\n"
                    header_size = len(file_header.encode('utf-8'))

                    # If adding the new file exceeds the max size, close the current file and create a new one
                    if current_size + file_size + header_size > max_size_bytes:
                        f_out.close()
                        output_index += 1
                        output_file = os.path.join(output_folder, f"output_{output_index}.txt")
                        f_out = open(output_file, "w")
                        current_size = 0

                    # Write the file's content and update the current size
                    f_out.write(file_header)
                    f_out.write(content)
                    f_out.write("\n\n" + "="*50 + "\n\n")
                    current_size += file_size + header_size

            except Exception as e:
                error_message = f"Error reading file {file}: {str(e)}\n\n" + "="*50 + "\n\n"
                if current_size + len(error_message.encode('utf-8')) > max_size_bytes:
                    f_out.close()
                    output_index += 1
                    output_file = os.path.join(output_folder, f"output_{output_index}.txt")
                    f_out = open(output_file, "w")
                    current_size = 0
                f_out.write(error_message)
                current_size += len(error_message.encode('utf-8'))

    f_out.close()
    print(f"All files from {folder_path} have been written to {output_folder}.")



def folder_to_text_file_big_exclude(folder_path, output_folder="multi_agent_llm_platform", max_file_size_mb=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_index = 1
    output_file = os.path.join(output_folder, f"output_{output_index}.txt")
    f_out = open(output_file, "w")
    current_size = 0
    max_size_bytes = max_file_size_mb * 1024 * 1024  # Convert MB to bytes

    # Directories to exclude

    exclude_dirs = {
        "node_modules",
        ".git",
        ".vscode",
        ".idea",
        ".husky",
        ".svelte-kit",
        "chart",
        "docs",

        "venv", "__pycache__"# Depending on context, may be irrelevant if it only contains static assets
    }
    # "scripts",
    # "static",
    #
    # Walk through the folder
    for root, dirs, files in os.walk(folder_path):
        # Exclude certain directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
                    content = f_in.read()

                    # Check the size of the current file to be written
                    file_size = len(content.encode('utf-8'))
                    file_header = f"File: {file}\nPath: {file_path}\n\n"
                    header_size = len(file_header.encode('utf-8'))

                    # If adding the new file exceeds the max size, close the current file and create a new one
                    if current_size + file_size + header_size > max_size_bytes:
                        f_out.close()
                        output_index += 1
                        output_file = os.path.join(output_folder, f"output_{output_index}.txt")
                        f_out = open(output_file, "w")
                        current_size = 0

                    # Write the file's content and update the current size
                    f_out.write(file_header)
                    f_out.write(content)
                    f_out.write("\n\n" + "="*50 + "\n\n")
                    current_size += file_size + header_size

            except Exception as e:
                error_message = f"Error reading file {file}: {str(e)}\n\n" + "="*50 + "\n\n"
                if current_size + len(error_message.encode('utf-8')) > max_size_bytes:
                    f_out.close()
                    output_index += 1
                    output_file = os.path.join(output_folder, f"output_{output_index}.txt")
                    f_out = open(output_file, "w")
                    current_size = 0
                f_out.write(error_message)
                current_size += len(error_message.encode('utf-8'))

    f_out.close()
    print(f"All files from {folder_path} have been written to {output_folder}.")


if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")  # Ask for the folder path input
    folder_to_text_file_big_exclude(folder_path)


