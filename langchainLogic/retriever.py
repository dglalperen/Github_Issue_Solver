import sys
from abc import ABC

from langchain import LLMChain, PromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from dotenv import load_dotenv
import os
from langchain.chains.retrieval_qa.base import BaseRetriever
from pydantic import BaseModel, Field
import numpy as np

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")


def get_docs(docs, files):
    essential_docs = [doc for doc in docs if doc.metadata['source'] in files]
    return sorted(essential_docs, key=lambda x: x.metadata['chunk_id'])


class MyRetriever(BaseRetriever, BaseModel, ABC):
    docs: list = Field(default_factory=list)
    readlock = False

    def __init__(self, docs=None, files=None, **kwargs):
        super().__init__(**kwargs)

        if files is None:
            files = [""]
        if docs:
            self.docs = self.process_docs(docs, files)

    def aget_relevant_documents(self, query: str):
        print("UNDEFINED ABSTRACT MEHTOD CALLED  aget_relevant_documents")
        return None

    def process_docs(self, docs, files):
        essential_docs = [doc for doc in docs if doc.metadata['source'] in files]
        return sorted(essential_docs, key=lambda x: x.metadata['chunk_id'])

    def get_relevant_documents(self, query):

        tempdb = DeepLake(embedding_function=OpenAIEmbeddings(disallowed_special=()), exec_option="python",
                          read_only=self.readlock)
        if not self.readlock:
            tempdb.add_documents(self.docs)
            self.readlock = True  # lock the db to prevent writing
        reldocs = tempdb.similarity_search(query=query, k=10)
        return reldocs


def CustomRetriever(files, dataset_path):
    # Laden Sie den VectorIndex mit den hochgeladenen Chunks
    embeddings = OpenAIEmbeddings(disallowed_special=())
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings, exec_option="python")
    docs = (db.similarity_search(query=" ", k=10000000))
    retriever = MyRetriever(docs=docs, files=files)
    context = get_docs(docs, files)
    return retriever, context


def deeplake_simsearch(embeddings, dataset_path, query, k):
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings, exec_option="python")
    docs = (db.similarity_search(query=query, k=k))
    return docs






# Beispiel zur Lösung eines Issues
dataset_path = "../vectordbs/chatbot"
issue = ''' a CNN should be used instead of the BERT model in the train.py script, because it can handle the type of data better.
The CNN should not be too complex, but also not too simple and should be generated using Tensorflow.
The CNN should be integrated into the logic and adapted according to the word vectors used. Change the code of it, as good as you can.'''

# Suche nach relevanten Dokumenten im DeepLake basierend auf dem gegebenen Issue
issue_documents = deeplake_simsearch(OpenAIEmbeddings(disallowed_special=()), dataset_path, issue, 5)

# Extrahiere die 'source'-Metadaten aus den gefundenen Dokumenten
retrieved_sources = [doc.metadata['source'] for doc in issue_documents]

# Entferne doppelte 'source'-Einträge, um eine eindeutige Liste zu erhalten
unique_sources = list(set(retrieved_sources))

# Liste der Dateien, die basierend auf Tags hinzugefügt werden sollen
additional_files = ['repos/chatbot/chatbot_project/functions.py', 'repos/chatbot/chatbot_project/train.py']

# Kombiniere die eindeutigen 'source'-Einträge mit den zusätzlichen Dateien, wobei Dopplungen vermieden werden
merged_sources = set(unique_sources).union(set(additional_files))

# Konvertiere das Set wieder in eine Liste
final_source_list = list(merged_sources)
print(final_source_list)
# Initialisiere das OpenAI-Chat-Modell
model = ChatOpenAI(model="gpt-4")

# Verwende die endgültige Liste der 'source'-Dateien, um den Retrieval-Prozess durchzuführen und den Kontext zu erhalten
# 1. retriever ist dafür da, um es der ConversationalRetrievalChain zu übergeben.
# 2. context ist dafür da, um es dem PromptTemplate zu übergeben.
# In diesem Beispiel wird 2. verwendet.
retriever, context = CustomRetriever(final_source_list, dataset_path)

# Initialisiere den Speicher für die Konversationshistorie
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Definiere die Vorlage für den Eingabeaufforderungs-Text
prompt_template = PromptTemplate(
    input_variables=["text"],
    template="""
{text}
"""
)

# Erstelle die Eingabe für die LLM-Kette, bestehend aus dem gegebenen Issue und dem Kontext (Code)
inputs = {
    "text": issue + str(context)
}

# Initialisiere und führe die Konversation aus
chain = LLMChain(llm=model, memory=memory, prompt=prompt_template, verbose=True)
result = chain.run(inputs)

# Drucke das Ergebnis
print(result)
