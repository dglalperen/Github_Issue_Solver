import requests
import json
import os

def fork_repo(github_token, repo_url):
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/forks"
    headers = {"Authorization": f"token {github_token}"}

    response = requests.post(api_url, headers=headers)
    if response.status_code == 202:  # Accepted
        forked_repo_url = response.json().get('html_url', '')
        print(f"Successfully forked {repo_url}")
        return forked_repo_url
    else:
        print(f"Failed to fork {repo_url}. Status code: {response.status_code}")
        return None



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


def main():
    github_token = "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"
    print(github_token)
    repo_url = "https://github.com/kaan9700/chatbot"
    
    forked_repo_url = fork_repo(github_token, repo_url)
    if(forked_repo_url == None):
        print("Forking failed")
        return
    print(f"Repo forked under: {forked_repo_url}")

if __name__ == "__main__":
    main()