import os

from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo

def promptLangchain(repoURL):

    os.environ['OPENAI_API_KEY'] = ""


    embeddings = OpenAIEmbeddings(disallowed_special=())

    db = DeepLake(indexRepo(repoURL), read_only=True, embedding_function=embeddings)

    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 100
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 10

    model = ChatOpenAI(model="gpt-3.5-turbo-0613")
    qa = ConversationalRetrievalChain.from_llm(model,retriever=retriever) # add verbose = True to see the full convo

    questions = [
        "Wie heißt das Projekt?",
        "Was ist das Ziel des Projekts?",

    ]
    chat_history = []
    for question in questions:
        result = qa({"question": question, "chat_history": chat_history})
        ##chat_history.append((question, result['answer']))
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")

        #append result into textfile in generatedDocs folder
        with open("../result/result.txt", "a") as myfile:
            myfile.write(result['answer']+"\n")
            myfile.close()
