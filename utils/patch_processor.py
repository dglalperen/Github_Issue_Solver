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


def apply_patch(source_file, patch_file):
    try:
        # Repository initialisieren, wenn es noch nicht existiert
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)

        parts = os.path.normpath(source_file).split(os.sep)

        # Die letzten 3 Teile des Pfades extrahieren
        desired_path = os.path.join(*parts[-3:])

        # Temporäre Datei erstellen, um den Inhalt von source_file zu kopieren
        temp_file = '../pull_code/' + desired_path

        # Stellen Sie sicher, dass das Verzeichnis existiert
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)

        with open(source_file, 'r') as f_in, open(temp_file, 'w') as f_out:
            f_out.write(f_in.read())

        # Datei zum Repo hinzufügen und committen
        subprocess.run(['git', 'add', temp_file], check=True)
        subprocess.run(['git', 'commit', '-m', 'Temporary commit'], check=True)

        # Patch anwenden
        with open(patch_file, 'r') as f:
            subprocess.run(['git', 'apply', '--whitespace=fix'], input=f.read(), text=True, check=True)

        # Aufräumen
        os.remove(temp_file)
        subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], check=True)  # Letzten Commit entfernen

    except subprocess.CalledProcessError:
        pass

    return True


if __name__ == '__main__':
    filename = '../result/result_chatbot.txt'
    # Beispielaufruf
    paare = process_result_txt(filename)
    # Aufruf der Funktion
    for paar in paare:

        apply_patch(paar['json']['source'], filename)


