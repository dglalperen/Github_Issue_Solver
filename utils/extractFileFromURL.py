def extractFilesFromURL(issueText, stripLineNumbers=True):
    print("Starting extractFileFromURL function...")
    # get repo name from issue
    repo_name = issueText["repository_url"].split("/")[-1]

    # Extract all URLS from the issue text
    urls = []
    for word in issueText["body"].split():
        if word.startswith("http"):
            strip_chars = ",.!'\"?"
            urls.append(word.rstrip(strip_chars))

    sanitized_urls = []
    # Check if the URL is a GitHub URL and linked to the repo
    for url in urls:
        if "github.com" in url and "blob" in url and repo_name in url:
            sanitized_urls.append(url)

    print(f"Sanitized URLs: {sanitized_urls}")
    filepaths = []
    # Extract the file path from the URL
    for san_urls in sanitized_urls:
        parts = san_urls.split("/")
        repo_index = parts.index(repo_name)
        # Construct the path from the parts after the repo name (excluding blob and main)
        file_path = "/".join(parts[repo_index:])
        file_path = file_path.replace("blob/main/", "")
        if stripLineNumbers:
            # remove the #L** from the file path
            file_path = '../repos/' + file_path.split("#")[0]
        filepaths.append(file_path)

    return filepaths

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
