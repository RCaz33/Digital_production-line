import os
import json
import sys

def anonymize_name(name, replacements):
    """
    Anonymizes a string (filename or directory name) by replacing
    occurrences of specified old strings with new ones.

    Args:
        name (str): The original name.
        replacements (dict): A dictionary mapping old strings to new strings.

    Returns:
        str: The anonymized name.
    """
    new_name = name
    for old, new in replacements.items():
        new_name = new_name.replace(old, new)
    return new_name

def anonymize_content(filepath, replacements):
    """
    Anonymizes the content of a Python file (.py), a Jupyter Notebook (.ipynb),
    or an HTML file (.html).

    For Python and HTML files, it reads the content, performs string replacements,
    and writes the modified content back if changes were made.

    For Jupyter Notebooks, it reads the JSON structure, iterates through
    cells (code and markdown), performs string replacements in the 'source'
    field (handling both string and list formats), and writes the modified
    JSON back if changes were made.

    Args:
        filepath (str): The path to the file.
        replacements (dict): A dictionary mapping old strings to new strings.
    """
    try:
        if filepath.endswith('.py') or filepath.endswith('.html') or filepath.endswith('.md'):
            # Process Python and HTML files
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            original_content = content
            for old, new in replacements.items():
                content = content.replace(old, new)
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Anonymized content in {filepath}")

        elif filepath.endswith('.ipynb'):
            # Process Jupyter Notebooks
            with open(filepath, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
            changed = False
            # Iterate through cells in the notebook
            for cell in notebook.get('cells', []):
                if 'source' in cell:
                    original_source = cell['source']
                    if isinstance(cell['source'], str):
                         # Handle single-string source
                         for old, new in replacements.items():
                            cell['source'] = cell['source'].replace(old, new)
                         if original_source != cell['source']:
                             changed = True
                    elif isinstance(cell['source'], list):
                        # Handle multi-line source (list of strings)
                        new_source_lines = []
                        source_changed_in_cell = False
                        for line in cell['source']:
                            original_line = line
                            for old, new in replacements.items():
                                line = line.replace(old, new)
                            new_source_lines.append(line)
                            if original_line != line:
                                source_changed_in_cell = True
                        cell['source'] = new_source_lines
                        if source_changed_in_cell:
                             changed = True

            if changed:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Use indent=1 for readability and ensure consistent output
                    # ensure_ascii=False allows non-ASCII characters to be written directly
                    json.dump(notebook, f, indent=1, ensure_ascii=False)
                print(f"Anonymized content in {filepath}")

        # else:
        #     print(f"Skipping unsupported file type for content anonymization: {filepath}") # Uncomment for more verbose output

    except FileNotFoundError:
        print(f"Error: File not found during content anonymization: {filepath}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {filepath}. Skipping content anonymization.", file=sys.stderr)
    except Exception as e:
        print(f"Error processing content for {filepath}: {e}", file=sys.stderr)


def main():
    """
    Main function to get the root directory from the user and start the
    anonymization process.
    """
    root_directory = input("Enter the root directory path: ")
    if not os.path.isdir(root_directory):
        print("Invalid directory path.")
        return

    # Get the absolute path and normalize it for reliable comparison later
    root_directory = os.path.abspath(root_directory)

    replacements = {
        "XX": "XX",
        "XY": "XY",
        "YY": "YY",
        "RE1": "RE1",
        "RE2": "RE2",
    }

    print(f"Starting anonymization process in {root_directory}...")

    # Walk the directory tree from bottom up (topdown=False)
    # This ensures files within a directory are processed before the directory
    # itself is potentially renamed.
    for dirpath, dirnames, filenames in os.walk(root_directory, topdown=False):
        # Anonymize files in the current directory first
        for filename in filenames:
            old_filepath = os.path.join(dirpath, filename)

            # Anonymize content of supported files (.py, .ipynb, .html)
            anonymize_content(old_filepath, replacements)

            # Anonymize the filename (applies to all files found)
            new_filename = anonymize_name(filename, replacements)
            new_filepath = os.path.join(dirpath, new_filename)

            # Rename the file if the name has changed
            if old_filepath != new_filepath:
                try:
                    # Check if the target path already exists and is the same file
                    if os.path.exists(new_filepath) and os.path.samefile(old_filepath, new_filepath):
                         # print(f"Path {old_filepath} and {new_filepath} are the same file. No rename needed.") # Uncomment for more verbose output
                         pass
                    # Check if the target path exists but is a different file/directory
                    elif os.path.exists(new_filepath):
                         print(f"Cannot rename file {old_filepath} to {new_filepath} because {new_filepath} already exists.", file=sys.stderr)
                    else:
                        os.rename(old_filepath, new_filepath)
                        print(f"Renamed file '{old_filepath}' to '{new_filepath}'")
                except FileNotFoundError:
                    print(f"Error: File not found during renaming: {old_filepath}", file=sys.stderr)
                except Exception as e:
                    print(f"Error renaming file {old_filepath}: {e}", file=sys.stderr)


        # Anonymize the current directory name, but skip the root directory
        # We compare against the absolute path of the root directory to be safe
        if os.path.abspath(dirpath) != root_directory:
            parent_dir = os.path.dirname(dirpath)
            dir_name = os.path.basename(dirpath)
            new_dir_name = anonymize_name(dir_name, replacements)
            new_dir_path = os.path.join(parent_dir, new_dir_name)

            # Rename the directory if the name has changed
            if dirpath != new_dir_path:
                 try:
                    # Check if the target path already exists and is the same directory
                    if os.path.exists(new_dir_path) and os.path.samefile(dirpath, new_dir_path):
                         # print(f"Path {dirpath} and {new_dir_path} are the same directory. No rename needed.") # Uncomment for more verbose output
                         pass
                    # Check if the target path exists but is a different file/directory
                    elif os.path.exists(new_dir_path):
                         print(f"Cannot rename directory {dirpath} to {new_dir_path} because {new_dir_path} already exists.", file=sys.stderr)
                    else:
                        os.rename(dirpath, new_dir_path)
                        print(f"Renamed directory '{dirpath}' to '{new_dir_path}'")
                 except FileNotFoundError:
                    print(f"Error: Directory not found during renaming: {dirpath}", file=sys.stderr)
                 except Exception as e:
                    print(f"Error renaming directory {dirpath}: {e}", file=sys.stderr)


    print("\nAnonymization process finished.")


if __name__ == "__main__":
    main()
