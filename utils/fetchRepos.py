import os

from git import Repo
def getRepo(repoURL):
    repoFolder = "repos/"
    print("Starting getRepo function...")
    name = repoURL.split("/")
    if not os.path.exists(repoFolder):
        print("Creating repos folder")
        os.makedirs(repoFolder + name[-1])
    if not os.path.exists(repoFolder + name[-1]):
        print("Cloning repo " + name[-1] + " to repos folder")
        Repo.clone_from(repoURL, repoFolder + name[-1])
    #checkoutBranch(repoFolder + name[-1])
    return str(repoFolder + name[-1])


def checkoutBranch(repo_path):
    try:
        repo = Repo(repo_path)
        if repo.bare:
            print("The repository is bare and does not have branches.")
            return

        # Fetch the latest updates from the remote repository
        repo.remotes.origin.fetch()

        branches = [str(branch) for branch in repo.branches]

        if not branches:
            print("No branches found in the repository.")
            return

        print("Available branches:")
        for i, branch in enumerate(branches):
            print(f"{i + 1}. {branch}")

        branch_choice = input("Enter the number of the branch you want to checkout: ")

        try:
            branch_choice = int(branch_choice)
            if 1 <= branch_choice <= len(branches):
                selected_branch = branches[branch_choice - 1]
                print(f"Checking out branch '{selected_branch}'...")
                repo.git.checkout(selected_branch)
                print(f"Successfully checked out branch '{selected_branch}'.")
            else:
                print("Invalid branch choice.")
        except ValueError:
            print("Invalid input. Please enter a valid branch number.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")