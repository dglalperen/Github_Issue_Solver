import os
import sys
from datetime import datetime
from handlers.IssueHandler import IssueHandler
from langchainLogic.prompt import promptLangchain
from dotenv import load_dotenv
from services.GitHubAPI import GithubAPI
from utils.extractFileFromURL import extractFilesFromURL
from utils.github_actions import fork_repo, create_pull_request
import traceback

# Load environment variables from .env file
load_dotenv()

# Get the necessary API keys from environment variables
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def save_response_to_file(issue_number, response):
    """Save the given response to a file with a timestamp."""
    try:
        date_str = datetime.now().strftime("%Y-%m-%d-%h-%m")
        file_name = f"Issue_{issue_number}_{date_str}.txt"
        with open(file_name, "w") as file:
            file.write(response)
        print(f"\nResponse saved to: {file_name}\n")
    except Exception as e:
        print(f"Failed to save the response to file: {e}")


def display_issue(issue):
    """Display the details of the given issue."""
    print(f'Issue #{issue["number"]}: {issue["title"]}')
    print(f'Created at: {issue["created_at"]}')
    print(f'Updated at: {issue["updated_at"]}')
    print(f'User: {issue["user"]["login"]}')
    print(f'Labels: {", ".join([label["name"] for label in issue["labels"]])}')
    print(f'URL: {issue["html_url"]}')
    print(f'\n{issue["body"]}\n')


def confirm_action(message):
    return input(f"{message} (y/n): ").strip().lower() == 'y'


if __name__ == "__main__":
    try:
        # Indicate the start of the main script
        print("Starting the main script...")

        # Check if the necessary API keys are available
        if not GITHUB_API_KEY or not OPENAI_API_KEY:
            print("API keys not set. Exiting.")
            exit(1)  # Exit with a non-zero status to indicate an error

        # Get the GitHub repository URL from the user
        #repo_url = input("Please enter the GitHub repository URL: ")
        original_repo_url = 'https://github.com/kaan9700/chatbot'
        forked_repo_url = ""
        if not original_repo_url:
            print("Repository URL not provided. Exiting.")
            exit(1)

        # Instantiate the GitHub API client
        github_api = GithubAPI()

        # Fetch and display the issues from the given repository URL
        print(f"Fetching issues from {original_repo_url}...")
        issues = github_api.get_issues(original_repo_url)
        if not issues:
            print("No issues found or an error occurred. Exiting.")
            exit(1)

        # Display the number of found issues
        print(f"Found {len(issues)} issues.")
        issue_handler = IssueHandler(issues)
        issue_handler.display_issues()

    except Exception as e:
        # Handle unexpected errors during initialization or API calls
        print(f"Initialization or API call failed: {e}")
        exit(1)

    # Extract the repository name from the provided URL
    repo_name = original_repo_url.split("/")[-1]

    # Continuously process issues until exit conditions are met
    while True:
        try:
            # Select an issue using the issue handler
            selected_issue = issue_handler.select_issue()

            if selected_issue:
                # Extract potential files related to the selected issue
                potentially_relevant_files, issue_body = extractFilesFromURL(selected_issue)
                print("Potentially relevant files: ", potentially_relevant_files)

                display_issue(selected_issue)

                # Get tags associated with the issue from the user
                tags = input("Please enter the tags for the issue, seperated with ',': ")
                tags_list = [tag.strip() for tag in tags.split(",")]

                # Get user input on files directly related to the issue
                related_files = input("Please enter the issue related files, seperated with ',': ")
                related_files_list = [related_file.strip() for related_file in related_files.split(",")]

                # If no files were provided, use the extracted files
                if related_files_list == ['']:
                    related_files_list = potentially_relevant_files
                else:
                    #https://github.com/kaan9700/chatbot/blob/main/chatbot_project/train.py,
                    # Combine user provided files with extracted files
                    #related_files_list = process_related_files(related_files_list, repo_name) + potentially_relevant_files
                    print("--")
                print("Related files: ", related_files_list)

                # Determine the conversation context type
                context_type = input("Do you want to use a retrieval (type --> retriever) or a context (type --> context) based Conversation: ")

                try:
                    # Ask the user if they want to fork the repository to further process the issue
                    user_decision = input("Do you want to fork and process the issue? (y/n): ")
                    if user_decision.lower() == 'y':
                        forked_repo_url = fork_repo(GITHUB_API_KEY, original_repo_url)
                        
                        # Process the selected issue with the provided context
                        promptLangchain(forked_repo_url, issue_body, tags_list, related_files_list, context_type)
                        
                        # Commit and push the changes to the forked repository
                        user_decision = input("Do you want to commit the generated code? (y/n): ")

                        if user_decision.lower() == 'y':
                            commit_message = input("Please enter the commit message: ")
                            branch_name = input("Please enter the branch name to push the changes: ")

                            # Assuming `github_api.commit_and_push` takes three arguments: repo_url, commit_message, and branch_name
                            github_api.commit_and_push(forked_repo_url, commit_message, branch_name)
                        else:
                            print("Skipping commit.")

                        
                        # Create a pull request with the generated code
                        user_decision = input("Do you want to create a pull request? (y/n): ")

                        if user_decision.lower() == 'y':
                            head_branch = input("Please enter the head branch name: ")
                            base_branch = input("Please enter the base branch name: ")
                            pr_title = input("Please enter the title for the pull request: ")
                            pr_body = input("Please enter the body for the pull request: ")
                            
                            create_pull_request(GITHUB_API_KEY, original_repo_url, head_branch, base_branch, pr_title, pr_body)
                        else:
                            print("Skipping pull request.")

                    else:
                        print("Skipping forking.")
                    
                    
                    
                except ValueError as ve:
                    # Handle potential errors during issue processing
                    import traceback
                    print(traceback.format_exc())
                    continue  # Continue to the next iteration to handle another issue

                # Indicate successful processing of the issue
                print("Issue processed and result saved in '../result/result.txt' file.")

                

            else:
                # If no issue was selected or user wishes to exit
                print("No selected issue or exiting.")
                break

        except Exception as e:
            # Handle unexpected errors during issue processing
            print(traceback.format_exc())



