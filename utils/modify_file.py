import os

def modify_file_replace_code(base_directory, relative_path, old_code_block, new_code_block):
    full_path = os.path.join(base_directory, relative_path)

    # Check if the file exists
    if not os.path.exists(full_path):
        print(f"File {full_path} does not exist!")
        return

    # Read the file
    try:
        with open(full_path, 'r') as f:
            lines = f.readlines()
            print("First 10 lines from file:", lines[:10])  # Debug line
    except Exception as e:
        print(f"Error reading file {full_path}: {e}")
        return

    # Split the code blocks into lines
    old_lines = old_code_block.strip().split('\n')
    print("Old lines:", old_lines)  # Debug line
    new_lines = new_code_block.strip().split('\n')

    # Search and replace
    i = 0
    replaced = False
    while i < len(lines):
        if lines[i].rstrip('\n') == old_lines[0]:
            match = True
            for j in range(1, len(old_lines)):
                if i + j >= len(lines) or lines[i + j].strip() != old_lines[j]:
                    match = False
                    break
            if match:
                print(f"Found matching code block at line {i + 1}. Replacing...")
                del lines[i:i + len(old_lines)]
                for j, new_line in enumerate(new_lines):
                    lines.insert(i + j, new_line + '\n')
                replaced = True
                break
        i += 1

    if not replaced:
        print(f"Could not find the specified code block in {full_path}. No changes made.")
        return

    # Write the modified content back to the file
    try:
        with open(full_path, 'w') as f:
            f.writelines(lines)
        print(f"Successfully modified {full_path}")
    except Exception as e:
        print(f"Error writing to file {full_path}: {e}")
 
    
if __name__ == "__main__":
    relative_path = "test.py"
    base_directory = "../repos/chatbot"
    old_code = """def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n)"""
        
    new_code = """def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)  # Corrected the base case"""

    modify_file_replace_code(base_directory, relative_path, old_code, new_code)

