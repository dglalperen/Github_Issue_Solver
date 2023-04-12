import requests
import json


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


def display_issue(issue):
    print(f'Issue #{issue["number"]}: {issue["title"]}')
    print(f'Created at: {issue["created_at"]}')
    print(f'Updated at: {issue["updated_at"]}')
    print(f'User: {issue["user"]["login"]}')
    print(f'Labels: {", ".join([label["name"] for label in issue["labels"]])}')
    print(f'URL: {issue["html_url"]}')
    print(f'\n{issue["body"]}\n')


if __name__ == '__main__':
    repo_url = 'https://github.com/ory/kratos-selfservice-ui-react-native'  # Replace with the repository URL
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
                else:
                    print('Invalid issue number.')

            except ValueError:
                print('Invalid input. Please enter a valid issue number.')
    else:
        print('No issues found or an error occurred.')
