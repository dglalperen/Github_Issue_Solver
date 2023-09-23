import os


def create_new_file(relative_path, initial_content):
    # Resolve the full path relative to the script
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

    # Check if file already exists
    if os.path.exists(full_path):
        print(f"File {full_path} already exists!")
        return

    # Create a new file and write initial content
    with open(full_path, 'w+') as f:
        f.write(initial_content)

    print(f"Successfully created {full_path}")
    