# GitHub Issue Solver

## Beschreibung

Dieses Projekt zielt darauf ab, GitHub-Issues automatisch zu analysieren und Lösungsvorschläge zu generieren. Mit der Unterstützung von KI-Technologien wie OpenAI's GPT-4 und der Datenverarbeitungsbibliothek DeepLake ermöglicht das Tool einen effizienten und automatisierten Workflow zur Bearbeitung von GitHub-Issues.

## Features

- Automatische Erfassung von GitHub-Issues aus einem angegebenen Repository
- DeepLake-Integration für effiziente Datenspeicherung und -verarbeitung
- Generierung von Lösungsvorschlägen durch KI-Technologie
- Möglichkeit, Pull Requests direkt aus dem Tool heraus zu erstellen
- Umfangreiches Error-Handling und Logging

## Technologien

- Python 3.x
- GitHub API
- OpenAI GPT-4
- DeepLake

## Voraussetzungen

- Python 3.x
- GitHub API-Token
- OpenAI API-Schlüssel
- DeepLake installiert

## Installation

1. **Repository klonen**

   ```bash
   git clone https://github.com/YourUsername/YourRepoName.git
   ```

2. **Abhängigkeiten installieren**

   ```bash
   pip install deeplake
   ```

3. **.env-Datei erstellen**

   Erstellen Sie eine `.env`-Datei im Root-Verzeichnis des Projekts und füllen Sie sie mit den erforderlichen API-Schlüsseln:

   ```env
   # .env
   GITHUB_API_KEY=Ihr_GitHub_API_Schlüssel
   OPENAI_API_KEY=Ihr_OpenAI_API_Schlüssel
   ```

## Nutzung

1. **Das Skript starten**

   ```bash
   python main.py
   ```

2. **GitHub-Repository-URL angeben**

3. **Ein Issue aus der Liste auswählen**

4. **Lösungsvorschläge werden generiert und gespeichert**

## Fehlerbehandlung und Logging

Das Tool verwendet ein umfangreiches Fehlerbehandlungs- und Logging-System, um maximale Zuverlässigkeit zu gewährleisten. Fehler und Ausnahmen werden detailliert protokolliert.

## Beiträge

Beiträge sind immer willkommen! Wenn Sie eine Idee oder einen Verbesserungsvorschlag haben, erstellen Sie bitte ein Issue oder einen Pull-Request.
