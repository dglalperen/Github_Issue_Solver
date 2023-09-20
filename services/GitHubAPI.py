import requests
class GithubAPI:
    def __init__(self, api_key):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {api_key}"
        }

    def get_issues(self, repo_url):
        repo_path = repo_url.replace("https://github.com/", "").rstrip(".git")
        api_url = f"https://api.github.com/repos/{repo_path}/issues"
        print(f"Fetching issues from: {api_url}")

        all_issues = []
        page = 1

        while True:
            params = {"page": page, "per_page": 100, "state": "open"}
            response = requests.get(api_url, headers=self.headers, params=params)

            if response.status_code == 200:
                issues = response.json()
                if not issues:
                    break
                all_issues.extend(issues)
                page += 1
            else:
                raise Exception(f"Error fetching issues. Status code: {response.status_code}")

        return all_issues
