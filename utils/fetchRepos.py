import os
import shutil


from git import Repo
def getRepo(repoURL):
    name = repoURL.split("/")
    if not os.path.exists("../repos/"):
        print("Creating repos folder")
        os.makedirs("../repos/" + name[-1])

    Repo.clone_from(repoURL, "../repos/" + name[-1])
    print("Cloned repo " + name[-1] + " to repos folder")
    return str("../repos/" + name[-1])
