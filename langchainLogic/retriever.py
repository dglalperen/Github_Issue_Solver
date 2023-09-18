from abc import ABC

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


class MyRetriever(BaseRetriever, BaseModel, ABC):
    docs: list = Field(default_factory=list)
    readlock = False
    def __init__(self, docs=None, files=[""], **kwargs):
        super().__init__(**kwargs)

        if docs:
            self.docs = self.process_docs(docs,files)

    # def get_relevant_documents(self, query: str):
    #     print("UNDEFINED ABSTRACT MEHTOD CALLED  get_relevant_documents")
    #     return None
    def aget_relevant_documents(self, query: str):
        print("UNDEFINED ABSTRACT MEHTOD CALLED  aget_relevant_documents")
        return None
    def process_docs(self, docs, files):
        essential_docs = [doc for doc in docs for file in files if file in doc.metadata['source']]
        return sorted(essential_docs, key=lambda x: x.metadata['chunk_id'])

    def get_relevant_documents(self, query):

        tempdb = DeepLake(embedding_function=OpenAIEmbeddings(disallowed_special=()), exec_option="python", read_only=self.readlock)
        if not self.readlock:
            tempdb.add_documents(self.docs)
            self.readlock = True # lock the db to prevent writing
        reldocs = tempdb.similarity_search(query=query, k=10)
        return reldocs

def CustomRetriever(files, dataset_path):
    # Laden Sie den VectorIndex mit den hochgeladenen Chunks
    #dataset_path = "../vectordbs/chatbot_doc"
    embeddings = OpenAIEmbeddings(disallowed_special=())
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings, exec_option="python")
    docs = (db.similarity_search(query=" ", k=10000000))

    retriever = MyRetriever(docs=docs, files=files)
    return retriever

def deeplakesimsearch(embeddings, dataset_path, query, k):
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings, exec_option="python")
    docs = (db.similarity_search(query=query, k=k))
    return docs

# model = ChatOpenAI(model="gpt-4")
# retriever = CustomRetriever(fil['aws'],)
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever, memory=memory, verbose=True)
# res = qa.run(
#     """
#     a CNN should be used instead of the BERT model in the train.py script, because it can handle the type of data better.
# The CNN should not be too complex, but also not too simple and should be generated using Tensorflow.
# The CNN should be integrated into the logic and adapted according to the word vectors used. Change the code of it, as good as you can.
#
# """
# )
# print(res)





