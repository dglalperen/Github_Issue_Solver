import os

from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo


def promptLangchain(repoURL, promptBody):
    print("Starting promptLangchain function...")

    os.environ["OPENAI_API_KEY"] = os.environ["API_KEY"]

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())

    print("Indexing repository...")
    db = DeepLake(indexRepo(repoURL), read_only=True, embedding_function=embeddings)

    print("Configuring retriever...")
    retriever = db.as_retriever()
    retriever.search_kwargs["distance_metric"] = "cos"
    retriever.search_kwargs["fetch_k"] = 100
    retriever.search_kwargs["maximal_marginal_relevance"] = True
    retriever.search_kwargs["k"] = 10

    print("Loading chat model...")
    model = ChatOpenAI(model="gpt-3.5-turbo-0613")
    qa = ConversationalRetrievalChain.from_llm(
        model, retriever=retriever
    )  # add verbose = True to see the full convo

    print("Preparing questions...")
    questions = [
        "Resolve the issue in the given text, which is delimited by XML tags. Print only the code for the solution. The issue is enclosed within: <Issue> "
        + promptBody
        + "</Issue>"
    ]

    print("Starting conversation retrieval...")
    chat_history = []
    for question in questions:
        result = qa({"question": question, "chat_history": chat_history})
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")

        print("Appending result to text file...")
        with open("../result/result.txt", "a") as myfile:
            myfile.write(result["answer"] + "\n")
            myfile.close()

    print("promptLangchain function completed.")
