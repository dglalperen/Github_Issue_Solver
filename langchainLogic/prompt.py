import os

from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo
from .retriever import CustomRetriever

def promptLangchain(repoURL, promptBody, tags, relevantFiles=[]):
    print("Starting promptLangchain function...")
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())

    print("Indexing repository...")
    #check if repo is already indexed
    ds_path = ""
    if os.path.exists("vectordbs/"+repoURL.split("/")[-1]):
        ds_path = "vectordbs/" + repoURL.split("/")[-1]
        print("repo already indexed")


    else:
        print("repo not indexed yet")
        ds_path = indexRepo(repoURL)

    print("Configuring retriever...")
    retriever = CustomRetriever(files=tags,dataset_path=ds_path)
    print("loaded retriever")

    print("Loading chat model...")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    model = ChatOpenAI(model="gpt-4")
    qa = ConversationalRetrievalChain.from_llm(
        model, retriever=retriever, memory=memory, verbose=False)  # add verbose = True to see the full convo
    questions = []

    if len(relevantFiles) > 0:
        questions.append("What are the files"+str(relevantFiles)+" about?")


    print("Preparing questions...")
    base_questions = [
        f"""Resolve the issue in the given text the best way you are able to, which is delimited by XML tags. Only print the Source code as answer. The issue is enclosed within: <Issue> "
        {promptBody}
        </Issue>
        Relevant information for the following questions is provided in the tags: {tags}""",
        "In which class should the previously generated code be placed?",
        'What are these code about and which files you can see?'
    ]
    questions.extend(base_questions)
    print("Starting conversation retrieval...")
    chat_history = []
    file_names = []
    for question in questions:
        result = qa({"question": question, "chat_history": chat_history})
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")

        print("Appending result to text file...")

        # save result to text file with reponame
        repo_name = repoURL.split("/")[-1]

        with open("result/result_" + repo_name + ".txt", "a") as myfile:
            myfile.write(result["answer"] + "\n")
            myfile.close()

    print("promptLangchain function completed.")
