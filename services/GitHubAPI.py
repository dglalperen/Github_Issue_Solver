import requests
import json
import git
from urllib.parse import urlparse

def extract_github_details(github_url):
    parsed_url = urlparse(github_url)
    path_elements = parsed_url.path.strip('/').split('/')
    
    if len(path_elements) >= 2:
        username = path_elements[0]
        repo_name = path_elements[1]
        return username, repo_name
    else:
        return None, None

class GithubAPI:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github+json"}
        
    def commit_and_push(self, forked_repo_url, commit_message, branch_name="main"):
        try:
            # Access the existing local repository
            username, repo_name = extract_github_details(forked_repo_url)
            local_path = f"../repos/{username}/{repo_name}"
            repo = git.Repo(local_path)
            
            # Check if the repo is dirty (i.e., has uncommitted changes)
            if repo.is_dirty():
                # Add all changes in tracked files to the staging area
                repo.git.add(update=True)

                # Commit the changes
                repo.git.commit('-m', commit_message)

            else:
                print("No changes to commit")

            # Set the URL for the remote repository if it is forked
            if forked_repo_url:
                remote = repo.create_remote('forked_origin', forked_repo_url)
            else:
                remote = repo.remotes.origin

            # Push the changes
            remote.push(branch_name)
        
        except git.exc.GitCommandError as e:
            print(f"An error occurred: {str(e)}")

    def get_issues(self, repo_url):
        repo_path = repo_url.replace("https://github.com/", "")
        api_url = f"https://api.github.com/repos/{repo_path}/issues"
        
        all_issues = []
        page = 1

        while True:
            params = {"page": page, "per_page": 100, "state": "open"}
            response = requests.get(api_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                issues = json.loads(response.text)
                if not issues:
                    break
                all_issues.extend(issues)
                page += 1
            else:
                print(f"Error: {response.status_code}")
                return None
                
        return all_issues
    
    
    
