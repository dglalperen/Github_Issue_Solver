import requests
import json

def fork_repo(github_token, repo_url):
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/forks"
    headers = {"Authorization": f"token {github_token}"}

    response = requests.post(api_url, headers=headers)
    if response.status_code == 202:  # Accepted
        print(f"Successfully forked {repo_url}")
    else:
        print(f"Failed to fork {repo_url}. Status code: {response.status_code}")



def create_pull_request(github_token, repo_url, head, base, title, body):
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/pulls"
    headers = {"Authorization": f"token {github_token}"}
    data = {
        "head": head,  # Der Branch, den du in den Basis-Branch mergen möchtest
        "base": base,  # Der Basis-Branch, in den gemerged werden soll
        "title": title,  # Der Titel des Pull Requests
        "body": body,  # Der Text, der den Pull Request beschreibt
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:  # Created
        print(f"Successfully created pull request: {response.json()['html_url']}")
    else:
        print(f"Failed to create pull request. Status code: {response.status_code}, Message: {response.json()['message']}")

