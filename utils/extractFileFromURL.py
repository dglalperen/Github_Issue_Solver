import os

def extractFilesFromURL(issueText, stripLineNumbers=True):
    """
    Extract file paths and URLs from the issue text.

    Args:
        issueText (dict): Dictionary containing the issue details.
        stripLineNumbers (bool): Flag to indicate whether line numbers from GitHub URLs should be removed.

    Returns:
        list: List of matching file paths and URLs from the repository.
    """

    # Extract repository name from the issue text
    repo_name = issueText["repository_url"].split("/")[-1]

    # List of valid file extensions
    fileextensions = [
        ".ts", ".json", ".js", ".jsx", ".tsx", ".html", ".css", ".scss", ".less", ".py", ".java", ".cpp", ".h", ".c",
        ".cs", ".go", ".php", ".rb", ".swift", ".kt", ".dart", ".rs", ".sh", ".txt"]

    potential_files = []

    # Identify potential files in the issue text based on their extensions
    for word in issueText["body"].split():
        shortend_word = word.rstrip(",.!'\"?")
        if shortend_word.endswith(tuple(fileextensions)):
            potential_files.append(shortend_word)

    print(f"Potential Files: {potential_files}")

    filepaths = []
    urls = []

    # Separate URLs and file paths from the potential files
    for file in potential_files:
        if file.startswith(("http", "www", "github.com")):
            urls.append(file)
        else:
            # If file doesn't start with '/', prepend it
            if not file.startswith("/"):
                file = "/" + file
            filepaths.append(file)

    sanitized_urls = []

    # Filter out URLs that aren't from GitHub or aren't linked to the repo
    for url in urls:
        if "github.com" in url and "blob" in url and repo_name in url:
            sanitized_urls.append(url)

    url_file_paths = []

    # Extract the file path from the sanitized URLs
    for san_urls in sanitized_urls:
        parts = san_urls.split("/")
        repo_index = parts.index(repo_name)
        # Construct the path from the parts after the repo name (excluding 'blob' and 'main')
        file_path = "/".join(parts[repo_index + 2:]) # +2 to skip repo_name and "blob"
        if stripLineNumbers:
            # Remove the #L** from the file path
            file_path = file_path.split("#")[0]
        file_path = '../repos/' + repo_name + '/' + file_path
        url_file_paths.append(file_path)

    path_final_files = []
    base_path = '../repos/' + repo_name

    # Look for matching file paths in the repo's directory
    for target in filepaths:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                if full_path.endswith(target) or os.path.basename(full_path) == target:
                    path_final_files.append(full_path)

    # Combine file paths from repo and from URLs and return
    return path_final_files + url_file_paths


def replaceURLsWithFilenames(issueBody):
    print("Starting replaceURLsWithFilenames function...")
    # Replace URLs noted in the issue body with their respective file names
    filenames = extractFilesFromURL(issueBody, stripLineNumbers=False)
    if len(filenames) == 0:
        return issueBody
    issueBody = issueBody["body"]
    for url in issueBody.split():
        if url.startswith("http"):
            for filename in filenames:
                if filename in url:
                    # extract line number from filename
                    if "#" in filename:
                        lineNum = filename.split("#L")[1]
                        filename = "(referenced file: " +filename.split("#L")[0] + " at line " + lineNum + ")"
                        issueBody = issueBody.replace(url, filename)


    return issueBody


if __name__ == "__main__":
    issueText = {'url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1', 'repository_url': 'https://api.github.com/repos/kaan9700/chatbot', 'labels_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/labels{/name}', 'comments_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/comments', 'events_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/events', 'html_url': 'https://github.com/kaan9700/chatbot/issues/1', 'id': 1893065161, 'node_id': 'I_kwDOHu0N8c5w1eHJ', 'number': 1, 'title': 'New Neural Net', 'user': {'login': 'kaan9700', 'id': 81586446, 'node_id': 'MDQ6VXNlcjgxNTg2NDQ2', 'avatar_url': 'https://avatars.githubusercontent.com/u/81586446?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/kaan9700', 'html_url': 'https://github.com/kaan9700', 'followers_url': 'https://api.github.com/users/kaan9700/followers', 'following_url': 'https://api.github.com/users/kaan9700/following{/other_user}', 'gists_url': 'https://api.github.com/users/kaan9700/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/kaan9700/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/kaan9700/subscriptions', 'organizations_url': 'https://api.github.com/users/kaan9700/orgs', 'repos_url': 'https://api.github.com/users/kaan9700/repos', 'events_url': 'https://api.github.com/users/kaan9700/events{/privacy}', 'received_events_url': 'https://api.github.com/users/kaan9700/received_events', 'type': 'User', 'site_admin': False}, 'labels': [], 'state': 'open', 'locked': False, 'assignee': None, 'assignees': [], 'milestone': None, 'comments': 0, 'created_at': '2023-09-12T18:42:13Z', 'updated_at': '2023-09-19T16:07:31Z', 'closed_at': None, 'author_association': 'OWNER', 'active_lock_reason': None, 'body':'a CNN should be /app/admin.py used instead of the BERT model in the train.py script, because it can handle the type of data better. The CNN should not be too complex, but also not too simple and should be generated using Tensorflow. The CNN should be integrated into the logic and adapted according to the word vectors used. https://github.com/kaan9700/chatbot/blob/main/chatbot_project/chat.py.', 'reactions': {'url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/reactions', 'total_count': 0, '+1': 0, '-1': 0, 'laugh': 0, 'hooray': 0, 'confused': 0, 'heart': 0, 'rocket': 0, 'eyes': 0}, 'timeline_url': 'https://api.github.com/repos/kaan9700/chatbot/issues/1/timeline', 'performed_via_github_app': None, 'state_reason': None}
    print(issueText["body"])
    test = extractFilesFromURL(issueText)
    print(test)