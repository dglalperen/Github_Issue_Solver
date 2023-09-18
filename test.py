import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchainLogic.indexer import indexRepo
from utils.fetchRepos import getRepo
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import pickle



def index_repo(repoURL):
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    # Set to true if you want to include documentation files
    documentation = True

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
        ".cs", ".go", ".php", ".rb", ".swift", ".kt", ".dart", ".rs", ".sh", ".yml", ".yaml", ".xml", ".txt"]

    if documentation:
        fileextensions.append("README.md")
        repo_name = repo_name + "_doc"
        print("added documentation files to ")

    docs = []
    chunk_file_name = []
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
                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    current_docs = loader.load_and_split()
                    for doc in current_docs:

                        chunk_file_name.append(file)
                        doc.metadata['file_name'] = file
                    docs.extend(current_docs)
                except Exception as e:
                    pass
    with open('chunk_file_names.pkl', 'wb') as file:
        pickle.dump(chunk_file_name, file)
    # chunk the files
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    texts = text_splitter.split_documents(docs)
    return texts





repoURL = 'https://github.com/kaan9700/chatbot'

print("Starting promptLangchain function...")
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

print("Initializing embeddings...")
embeddings = OpenAIEmbeddings(disallowed_special=())

texts = index_repo(repoURL)
