import re

def extract_urls_and_paths(text):
    fileextensions = [
        ".ts", ".json", ".js", ".jsx", ".tsx", ".html", ".css", ".scss", ".less", ".py", ".java", ".cpp", ".h", ".c",
        ".cs", ".go", ".php", ".rb", ".swift", ".kt", ".dart", ".rs", ".sh", ".txt"]

    # Regulärer Ausdruck zum Finden von URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)

    # Regulärer Ausdruck zum Finden von Dateipfaden
    path_pattern = "|".join([r'(?<!/)\.\./[^\s]+' + re.escape(ext) + r'|[^/\s]+' + re.escape(ext) for ext in fileextensions])
    paths = re.findall(path_pattern, text)

    extracted_items = urls + paths

    # Ersetzen von gefundenen URLs und Dateipfaden im Text
    for item in extracted_items:
        for ext in fileextensions:
            if item.endswith(ext):
                text = text.replace(item, item.split("/")[-1].replace(ext, "") + " file")

    # Entferne mehrfache Leerzeichen
    text = ' '.join(text.split())

    return text, extracted_items

def preprocess_query(query):
    def replace_with_descriptor(match_obj):
        full_match = match_obj.group(0)
        ext = full_match.split(".")[-1].capitalize() + "-File"
        return full_match + " " + ext

    # Combine both patterns
    combined_pattern = r"(([\w\-]+\/)+[\w\-]+\.\w+)|\b(?<!/)(\w+\.\w+)\b"

    # Use the `re.sub` method to replace matches in the string
    return re.sub(combined_pattern, replace_with_descriptor, query)



# Test
text = '''a CNN should be used instead of the BERT model in the ../repos/chatbot/chatbot_project/train.py file, because it can handle the type of data better.
Use the ../config/settings.ts config for TypeScript and check the ../assets/styles/main.scss for styling.
The CNN should be integrated into the logic and adapted according to the word vectors used. Change the code of it, as good as you can.'''

edited_text, extracted_list = extract_urls_and_paths(text)
print(edited_text)
print(extracted_list)
