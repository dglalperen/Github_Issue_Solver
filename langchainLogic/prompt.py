import os

from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo


def promptLangchain(repoURL, promptBody, relevantFiles = []):
    print("Starting promptLangchain function...")
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())

    print("Indexing repository...")
    #check if repo is already indexed
    if os.path.exists("vectordbs/"+repoURL.split("/")[-1]+"_doc"):
        print("repo already indexed")
        db = DeepLake(dataset_path="vectordbs/"+repoURL.split("/")[-1]+"_doc", embedding_function=embeddings)

    else:
        print("repo not indexed yet")
        #db = DeepLake(dataset_path=indexRepo(repoURL), embedding_function=embeddings)

    print("Configuring retriever...")
    retriever = db.as_retriever()
    retriever.search_kwargs['score_threshold'] = 0.8
    retriever.search_kwargs['fetch_k'] = 100
    retriever.search_kwargs['search_type'] = 'mmr'
    retriever.search_kwargs['lambda_mult'] = '0.7'
    retriever.search_kwargs['k'] = 25
    print("loaded retriever")

    print("Loading chat model...")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    model = ChatOpenAI(model="gpt-4")
    qa = ConversationalRetrievalChain.from_llm(
        model, retriever=retriever, memory=memory
    )  # add verbose = True to see the full convo
    questions = []
    if len(relevantFiles) > 0:
        questions.append("What are the files"+str(relevantFiles)+" about?")

    print("Preparing questions...")
    base_questions = [
        "Resolve the issue in the given text the best way you are able to, which is delimited by XML tags. Only print the Source code as answer. The issue is enclosed within: <Issue> "
        + promptBody
        + "</Issue>",
        "In which class should the previously generated code be placed?"
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
