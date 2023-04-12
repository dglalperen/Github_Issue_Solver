import requests
import json
import openai
import os
from datetime import datetime

# Get the value of an environment variable
api_key = os.environ['API_KEY']
openai.api_key = api_key

def get_issues_from_github_repo(repo_url):
    repo_path = repo_url.replace('https://github.com/', '')
    api_url = f'https://api.github.com/repos/{repo_path}/issues'
    headers = {'Accept': 'application/vnd.github+json'}

    all_issues = []
    page = 1

    while True:
        params = {'page': page, 'per_page': 100, 'state': 'open'}
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            issues = json.loads(response.text)
            if not issues:  # If no more issues, break the loop
                break

            all_issues.extend(issues)
            page += 1
        else:
            print(f'Error: {response.status_code}')
            return None

    return all_issues


def ask_chatgpt(prompt, context=None):
    messages = [{"role": "system",
                 "content": "You are an AI language model, and your task is to help users with their GitHub issues."}]

    if context:
        messages.append({"role": "user", "content": context})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    message = response['choices'][0]['message']['content']
    return message


def save_response_to_file(issue_number, response):
    date_str = datetime.now().strftime("%Y-%m-%d-%h-%m")
    file_name = f'Issue_{issue_number}_{date_str}.txt'

    with open(file_name, 'w') as file:
        file.write(response)

    print(f'\nResponse saved to: {file_name}\n')


def display_issue(issue):
    print(f'Issue #{issue["number"]}: {issue["title"]}')
    print(f'Created at: {issue["created_at"]}')
    print(f'Updated at: {issue["updated_at"]}')
    print(f'User: {issue["user"]["login"]}')
    print(f'Labels: {", ".join([label["name"] for label in issue["labels"]])}')
    print(f'URL: {issue["html_url"]}')
    print(f'\n{issue["body"]}\n')


if __name__ == '__main__':
    repo_url = input("Please enter the GitHub repository URL: ")
    issues = get_issues_from_github_repo(repo_url)

    if issues:
        for issue in issues:
            print(f'#{issue["number"]}: {issue["title"]}')

        while True:
            try:
                selected_issue_number = int(input("\nEnter the issue number you want to view (0 to exit): "))
                if selected_issue_number == 0:
                    break

                selected_issue = next((issue for issue in issues if issue['number'] == selected_issue_number), None)
                if selected_issue:
                    display_issue(selected_issue)

                    context = f'The GitHub repository URL is "{repo_url}".'
                    prompt = f'Please help me understand the following GitHub issue and suggest a possible solution: "{selected_issue["title"]}". The issue description is: "{selected_issue["body"]}".'

                    response = ask_chatgpt(prompt, context)
                    print(f'\nChatGPT response: {response}\n')

                    save_response_to_file(selected_issue["number"], response)
                else:
                    print('Invalid issue number.')

            except ValueError:
                print('Invalid input. Please enter a valid issue number.')
    else:
        print('No issues found or an error occurred.')
