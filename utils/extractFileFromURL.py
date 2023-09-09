def extractFilesFromURL(issueText, stripLineNumbers=True):
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
        if stripLineNumbers:
            # remove the #L** from the file name
            file_name = file_name.split("#")[0]
        filenames.append(file_name)
        print(f"File name: {file_name}")

    return filenames

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
