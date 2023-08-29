import requests
import json
import os
from datetime import datetime

from langchainLogic.prompt import promptLangchain

# Get the value of an environment variable
api_key = os.environ["API_KEY"]
os.environ["OPENAI_API_KEY"] = api_key  # Make sure the proper API key is set


def get_issues_from_github_repo(repo_url):
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/issues"
    headers = {"Accept": "application/vnd.github+json"}

    all_issues = []
    page = 1

    while True:
        params = {"page": page, "per_page": 100, "state": "open"}
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            issues = json.loads(response.text)
            if not issues:  # If no more issues, break the loop
                break

            all_issues.extend(issues)
            page += 1
        else:
            print(f"Error: {response.status_code}")
            return None

    return all_issues


def ask_chatgpt(prompt, context=None):
    messages = [
        {
            "role": "system",
            "content": "You are an AI language model specializing in software development, with a focus on assisting users in resolving their GitHub issues. Utilizing your expertise in coding best practices and software design patterns, your task is to analyze problems, suggest solutions, and guide users in implementing fixes for their GitHub-related challenges.",
        }
    ]

    if context:
        messages.append({"role": "user", "content": context})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)

    message = response["choices"][0]["message"]["content"]
    return message


def save_response_to_file(issue_number, response):
    date_str = datetime.now().strftime("%Y-%m-%d-%h-%m")
    file_name = f"Issue_{issue_number}_{date_str}.txt"

    with open(file_name, "w") as file:
        file.write(response)

    print(f"\nResponse saved to: {file_name}\n")


def display_issue(issue):
    print(f'Issue #{issue["number"]}: {issue["title"]}')
    print(f'Created at: {issue["created_at"]}')
    print(f'Updated at: {issue["updated_at"]}')
    print(f'User: {issue["user"]["login"]}')
    print(f'Labels: {", ".join([label["name"] for label in issue["labels"]])}')
    print(f'URL: {issue["html_url"]}')
    print(f'\n{issue["body"]}\n')

def get_issue_body(issue):
    print(f'\n{issue["body"]}\n')
    return issue["body"]

if __name__ == "__main__":
    print("Starting the main script...")

    repo_url = input("Please enter the GitHub repository URL: ")
    print(f"Fetching issues from {repo_url}...")
    issues = get_issues_from_github_repo(repo_url)

    if issues:
        print(f"Found {len(issues)} issues.")
        for issue in issues:
            print(f'#{issue["number"]}: {issue["title"]}')

        while True:
            selected_issue_number_input = input(
                "\nEnter the issue number you want to view (0 to exit): "
            )
            try:
                selected_issue_number = int(selected_issue_number_input)
                if selected_issue_number == 0:
                    break

                selected_issue = next(
                    (
                        issue
                        for issue in issues
                        if issue["number"] == selected_issue_number
                    ),
                    None,
                )
                if selected_issue:
                    display_issue(selected_issue)
                    issue_body = selected_issue["body"]
                    try:
                        promptLangchain(
                            repo_url, issue_body
                        )  # Process the selected issue
                    except ValueError as ve:
                        print(f"ValueError in promptLangchain function: {ve}")
                        continue
                    print(
                        "Issue processed and result saved in '../result/result.txt' file."
                    )
                else:
                    print("Invalid issue number.")
            except ValueError:
                print(
                    f"Invalid input: {selected_issue_number_input}. Please enter a valid issue number."
                )
    else:
        print("No issues found or an error occurred.")
