import os

from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo


def promptRefineLangchain(repoURL, relevantFiles = [], tags = []):
    print("Starting promptLangchain function...")
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())
    db = DeepLake(dataset_path="vectordbs/"+repoURL.split("/")[-1]+"_doc", embedding_function=embeddings)

    print("Configuring retriever...")
    retriever = db.as_retriever()
    retriever.search_kwargs['score_threshold'] = 0.8
    retriever.search_kwargs['fetch_k'] = 100
    retriever.search_kwargs['search_type'] = 'mmr'
    retriever.search_kwargs['lambda_mult'] = '0.7'
    retriever.search_kwargs['k'] = 20
    print("loaded retriever")

    #open result file of the repo
    with open("result/result_" + repoURL.split("/")[-1] + ".txt", "r") as myfile:
        result = myfile.read()
        myfile.close()

    print("Loading chat model...")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    model = ChatOpenAI(model="gpt-4")

    #read code.txt file
    with open("result/code.txt", "r") as myfile:
        code = myfile.read()
        myfile.close()

    text = input("Please enter what you want different in your code: ")


    qa = ConversationalRetrievalChain.from_llm(
        model, retriever=retriever, memory=memory, verbose=True
    )  # add verbose = True to see the full convo
    questions = []
    base_questions = [
        text+" (code is contained within the text)"+result,
    ]
    questions.extend(base_questions)
    print("Starting conversation retrieval...")
    chat_history = []
    file_names = []
    for question in questions:
        result2 = qa({"question": question, "chat_history": chat_history})
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result2['answer']} \n")

        print("Appending result to text file...")

        # save result to text file with reponame
        repo_name = repoURL.split("/")[-1]

        with open("result/result_" + repo_name + "_refined1.txt", "a") as myfile:
            myfile.write(result2["answer"] + "\n")
            myfile.close()

    print("promptLangchain function completed.")
