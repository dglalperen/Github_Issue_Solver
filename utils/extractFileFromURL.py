import os


def extractFilesFromURL(issueText, stripLineNumbers=True):
    """
    Extract file paths and URLs from the issue text and replace them in the issue body.

    Args:
        issueText (dict): Dictionary containing the issue details.
        stripLineNumbers (bool): Flag to indicate whether line numbers from GitHub URLs should be removed.

    Returns:
        list, str: List of matching file paths and URLs from the repository and the modified issue body.
    """

    # Extract repository name from the issue text
    repo_name = issueText["repository_url"].split("/")[-1]
    issueBody = issueText["body"]

    # List of valid file extensions
    fileextensions = (".ts", ".json", ".js", ".jsx", ".tsx", ".html", ".css", ".scss", ".less", ".py",
                      ".java", ".cpp", ".h", ".c", ".cs", ".go", ".php", ".rb", ".swift", ".kt", ".dart",
                      ".rs", ".sh", ".txt")

    # Identify potential files in the issue text based on their extensions
    potential_files = [word.rstrip(",.!'\"?") for word in issueBody.split() if
                       word.rstrip(",.!'\"?").endswith(fileextensions)]

    filepaths = []
    urls = []
    original_paths = []
    # Separate URLs and file paths from the potential files
    for file in potential_files:
        if file.startswith(("http", "www", "github.com")):
            urls.append(file)
        else:

            original_paths.append(file)
            file = file.lstrip('.') if file.startswith(".") else file
            file = file if file.startswith("/") or file.startswith("./") else "/" + file
            filepaths.append(file)

    # Filter out URLs that aren't from GitHub or aren't linked to the repo
    sanitized_urls = [url for url in urls if "github.com" in url and "blob" in url and repo_name in url]

    url_file_paths = []
    base_path = f'./repos/{repo_name}'

    # Extract the file path from the sanitized URLs and replace URLs in the issue body with these paths
    for san_url in sanitized_urls:
        parts = san_url.split("/")
        repo_index = parts.index(repo_name)
        file_path = "/".join(parts[repo_index + 2:])  # +2 to skip repo_name and "blob"
        file_path = file_path.split("#")[0] if stripLineNumbers else file_path
        file_path = f'{base_path}/{file_path}'
        url_file_paths.append(file_path)
        issueBody = issueBody.replace(san_url, file_path)

    path_final_files = []

    # Look for matching file paths in the repo's directory
    for target in filepaths:

        for root, dirs, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                if full_path.endswith(target) or os.path.basename(full_path) == target:
                    path_final_files.append(full_path)



    # Replace original paths in the issue body with their corresponding paths from the rep
    for path in original_paths:
        result = [os.path.basename(string) for string in path_final_files if
                  os.path.basename(string) == os.path.basename(path)]

        issueBody = issueBody.replace(path, ' and/or '.join(result))

    output = path_final_files + url_file_paths
    output = [
        ('../' + elem[2:]) if elem.startswith('./') else ('../' + elem) if not elem.startswith('../') else elem for elem
        in output]

    # Return the list of file paths and the modified issue body
    return output, issueBody




if __name__ == "__main__":
    issueText = {'url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1', 'repository_url': 'https://api.github.com/repos/kaan9700/chatbot', 'labels_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/labels{/name}', 'comments_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/comments', 'events_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/events', 'html_url': 'https://github.com/kaan9700/chatbot/issues/1', 'id': 1893065161, 'node_id': 'I_kwDOHu0N8c5w1eHJ', 'number': 1, 'title': 'New Neural Net', 'user': {'login': 'kaan9700', 'id': 81586446, 'node_id': 'MDQ6VXNlcjgxNTg2NDQ2', 'avatar_url': 'https://avatars.githubusercontent.com/u/81586446?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/kaan9700', 'html_url': 'https://github.com/kaan9700', 'followers_url': 'https://api.github.com/users/kaan9700/followers', 'following_url': 'https://api.github.com/users/kaan9700/following{/other_user}', 'gists_url': 'https://api.github.com/users/kaan9700/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/kaan9700/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/kaan9700/subscriptions', 'organizations_url': 'https://api.github.com/users/kaan9700/orgs', 'repos_url': 'https://api.github.com/users/kaan9700/repos', 'events_url': 'https://api.github.com/users/kaan9700/events{/privacy}', 'received_events_url': 'https://api.github.com/users/kaan9700/received_events', 'type': 'User', 'site_admin': False}, 'labels': [], 'state': 'open', 'locked': False, 'assignee': None, 'assignees': [], 'milestone': None, 'comments': 0, 'created_at': '2023-09-12T18:42:13Z', 'updated_at': '2023-09-19T16:07:31Z', 'closed_at': None, 'author_association': 'OWNER', 'active_lock_reason': None,
                 'body':
                     ''' 
                     a CNN should be used instead of the BERT model in the ./chatbot_project/train.py script, because it can handle the type of data better.
                    The CNN should not be too complex, but also not too simple and should be generated using Tensorflow. The CNN should be integrated into the logic and adapted according to the word vectors used.
                    Also print in the chat.py at the end :
                    print(‚hello world‘)
                    This ist extremely important
                     
                     ''',
                     'reactions': {'url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/reactions', 'total_count': 0, '+1': 0, '-1': 0, 'laugh': 0, 'hooray': 0, 'confused': 0, 'heart': 0, 'rocket': 0, 'eyes': 0}, 'timeline_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/timeline', 'performed_via_github_app': None, 'state_reason': None}
    test, body = extractFilesFromURL(issueText)
    print(test)



