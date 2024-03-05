import re
import os
import subprocess
import sys

def process_result_txt(pfad_zur_datei):
    # Datei einlesen
    with open(pfad_zur_datei, 'r') as datei:
        inhalt = datei.read()

    # Regulärer Ausdruck, um das JSON-Muster sowie den dazugehörigen Code zu identifizieren
    muster = r'(.*?)(\{\s*"source"\s*:\s*"(.+?)"\s*\})'

    # Flags hinzufügen, um den Suchvorgang über mehrere Zeilen hinweg auszuführen
    matches = re.findall(muster, inhalt, re.DOTALL | re.IGNORECASE)
    code_json_paare = []
    for match in matches:
        code, json_str, source = match
        json_obj = {
            "source": source
        }
        code_json_paare.append({
            "code": code.strip(),
            "json": json_obj
        })

    return code_json_paare

def replace_file_content(file_path, new_content):
    """
    Replaces the content of a file.

    Parameters:
    - file_path: Path to the file whose content should be replaced.
    - new_content: The new content to fill the file with.
    """
    print(f"Replacing content of file '{file_path}'...")
    with open(file_path, 'w') as file:
        file.write(new_content)




if __name__ == '__main__':
    filename = '../result/result_chatbot.txt'
    # Beispielaufruf
    paare = process_result_txt(filename)
    # Aufruf der Funktion
    for paar in paare:

        replace_file_content(paar['json']['source'], paar['code'])


