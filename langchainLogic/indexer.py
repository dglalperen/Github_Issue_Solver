import os

from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake, Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from utils.fetchRepos import getRepo


#from src.utils.fetchRepos import getTestRepo,readFromExcel

def indexRepo(repoURL):
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    # Set to true if you want to include documentation files

    embeddings = OpenAIEmbeddings(disallowed_special=())
    repoDir = getRepo(repoURL)

    # load files in repo
    root_dir = repoDir
    print("project directory is: " + root_dir)
    # get name of repo
    repo_name = root_dir.split("/")[-1]
    print("repo name is: " + repo_name)

    # check if repo is already indexed
    if os.path.exists("vectordbs/" + repo_name):
        print("repo already indexed")
        return str("vectordbs/" + repo_name)

    fileextensions = [
        ".ts", ".json", ".js", ".jsx", ".tsx", ".html", ".css", ".scss", ".less", ".py", ".java", ".cpp", ".h", ".c",
        ".cs", ".go", ".php", ".rb", ".swift", ".kt", ".dart", ".rs", ".sh", ".txt"]

    docs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            # ignore node_modules and package-lock.json
            if ("node_modules" in dirpath or
                    '.idea' in dirpath or
                    '__pycache__' in dirpath or
                    "package-lock.json" in file):
                continue
            # ignore files that are not of the specified file extensions
            if file.endswith(tuple(fileextensions)):
                print(file)
                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    current_docs = loader.load_and_split()
                    for doc in current_docs:
                        doc.metadata['file_name'] = file
                    docs.extend(current_docs)
                except Exception as e:
                    pass

    # chunk the files
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    texts = text_splitter.split_documents(docs)

    # Adding chunk ID to metadata
    for idx, text in enumerate(texts):
        text.metadata['chunk_id'] = idx
        print(text.metadata['file_name'], text.metadata['chunk_id'])

    print("Number of chunks: ", len(texts))
    # embed the files and add them to the vector db
    db = DeepLake(dataset_path="vectordbs/" + repo_name, embedding_function=embeddings)
    db.add_documents(texts)

    return str("vectordbs/" + repo_name)
