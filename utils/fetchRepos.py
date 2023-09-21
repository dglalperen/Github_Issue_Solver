import os
import shutil


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
    return str(repoFolder + name[-1])
