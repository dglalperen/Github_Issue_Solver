import os
from datetime import datetime
from handlers.IssueHandler import IssueHandler
from langchainLogic.prompt import promptLangchain
from dotenv import load_dotenv
from services.GitHubAPI import GithubAPI
from utils.extractFileFromURL import extractFilesFromURL
from utils.github_actions import fork_repo, create_pull_request

load_dotenv()

# ERSETZE DURCH .env file
# Get the value of an environment variable
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def save_response_to_file(issue_number, response):
    try:
        date_str = datetime.now().strftime("%Y-%m-%d-%h-%m")
        file_name = f"Issue_{issue_number}_{date_str}.txt"
        with open(file_name, "w") as file:
            file.write(response)
        print(f"\nResponse saved to: {file_name}\n")
    except Exception as e:
        print(f"Failed to save the response to file: {e}")


def display_issue(issue):
    print(f'Issue #{issue["number"]}: {issue["title"]}')
    print(f'Created at: {issue["created_at"]}')
    print(f'Updated at: {issue["updated_at"]}')
    print(f'User: {issue["user"]["login"]}')
    print(f'Labels: {", ".join([label["name"] for label in issue["labels"]])}')
    print(f'URL: {issue["html_url"]}')
    print(f'\n{issue["body"]}\n')


if __name__ == "__main__":
    try:
        print("Starting the main script...")

        GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not GITHUB_API_KEY or not OPENAI_API_KEY:
            print("API keys not set. Exiting.")
            exit(1)

        repo_url = input("Please enter the GitHub repository URL: ")
        if not repo_url:
            print("Repository URL not provided. Exiting.")
            exit(1)

        github_api = GithubAPI()

        print(f"Fetching issues from {repo_url}...")
        issues = github_api.get_issues(repo_url)
        if not issues:
            print("No issues found or an error occurred. Exiting.")
            exit(1)

        print(f"Found {len(issues)} issues.")

        issue_handler = IssueHandler(issues)
        issue_handler.display_issues()

    except Exception as e:
        print(f"Initialization or API call failed: {e}")
        exit(1)

    while True:
        try:
            selected_issue = issue_handler.select_issue()

            if selected_issue:
                potentially_relevant_files = extractFilesFromURL(selected_issue)
                display_issue(selected_issue)
                issue_body = selected_issue["body"]

                try:
                    promptLangchain(repo_url, issue_body)  # Process the selected issue
                except ValueError as ve:
                    print(f"ValueError in promptLangchain function: {ve}")
                    continue

                print("Issue processed and result saved in '../result/result.txt' file.")

                # Fork the repo here if user agrees
                user_decision = input("Do you want to fork the repository? (y/n): ")
                if user_decision.lower() == 'y':
                    fork_repo(GITHUB_API_KEY, repo_url)
                else:
                    print("Skipping forking.")

            else:
                print("No selected issue or exiting.")
                break

        except Exception as e:
            print(f"An error occurred while processing the issue: {e}")
