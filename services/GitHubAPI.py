import requests
import json

class GithubAPI:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github+json"}

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