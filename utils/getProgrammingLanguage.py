import magic

def get_programming_language(file_path):
    mime_type = magic.from_file(file_path, mime=True)
    if mime_type == 'text/x-python':
        return 'Python'
    elif mime_type == 'text/javascript':
        return 'JavaScript'
    # Add more conditions for other programming languages

    return 'Unknown'

file_path = '/path/to/your/code/file'
programming_language = get_programming_language(file_path)
print(f"The programming language of the file is: {programming_language}")