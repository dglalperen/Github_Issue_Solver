import os
import shutil


from git import Repo
def getRepo(repoURL):
    print("Starting getRepo function...")
    name = repoURL.split("/")
    if not os.path.exists("repos/"):
        print("Creating repos folder")
        os.makedirs("repos/" + name[-1])
    if not os.path.exists("repos/" + name[-1]):
        print("Cloning repo " + name[-1] + " to repos folder")
        Repo.clone_from(repoURL, "repos/" + name[-1])
    return str("repos/" + name[-1])
