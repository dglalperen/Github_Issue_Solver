def extractFilesFromURL(issueText):
    print("Starting extractFileFromURL function...")
    # get repo name from issue
    repo_name = issueText["repository_url"].split("/")[-1]

    # Extract all URLS from the issue text
    urls = []
    for word in issueText["body"].split():
        if word.startswith("http"):
            urls.append(word)

    sanitized_urls = []
    # Check if the URL is a GitHub URL and linked to the repo
    for url in urls:
        if "github.com" in url and "blob" and repo_name in url:
            sanitized_urls.append(url)

    print(f"Sanitized URLs: {sanitized_urls}")
    filenames = []
    # Extract the file name from the URL
    for san_urls in sanitized_urls:
        file_name = san_urls.split("/")[-1]
        # remove the #L** from the file name
        file_name = file_name.split("#")[0]
        filenames.append(file_name)
        print(f"File name: {file_name}")

    return filenames
