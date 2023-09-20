import sys
from abc import ABC

from langchain import LLMChain, PromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import SelfQueryRetriever
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

        tempdb = DeepLake(embedding=OpenAIEmbeddings(disallowed_special=()), exec_option="python",
                          read_only=self.readlock)
        if not self.readlock:
            tempdb.add_documents(self.docs)
            self.readlock = True  # lock the db to prevent writing
        reldocs = tempdb.similarity_search(query=query, k=10)
        return reldocs


def CustomRetriever(files, dataset_path,issue):
    # Laden Sie den VectorIndex mit den hochgeladenen Chunks
    #dataset_path = "../vectordbs/chatbot_doc"

    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="The soruce file the chunk was extracted from",
            type="string",
        ),
        AttributeInfo(
            name="file_name",
            description="The name of the file the chunk was extracted from",
            type="string",
        ),
        AttributeInfo(
            name="chunk_id",
            description="the id of the chunk",
            type="string",
        ),
    ]
    document_content_description = "The sourcecode of a project"
    model = ChatOpenAI(model="gpt-4")

    embeddings = OpenAIEmbeddings(disallowed_special=())
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding=embeddings, exec_option="python")
    docs = (db.similarity_search(query=" ", k=10000000))
    retriever = SelfQueryRetriever.from_llm(
        model, db, document_content_description, metadata_field_info, verbose=True
    )
    print(retriever.get_relevant_documents("What documents contain code to resolve the following issue? ->"+issue + "(relevant tags are: "+str(files)+")"))


    retriever = MyRetriever(docs=docs, files=files)
    context = get_docs(docs, files)
    return retriever, context


def deeplake_simsearch(embeddings, dataset_path, query, k):
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings, exec_option="python")
    docs = (db.similarity_search(query=query, k=k))
    return docs

"""files = ['train.py']
dataset_path = "../vectordbs/chatbot"
CustomRetriever(files, dataset_path," a CNN should be used instead of the BERT model in the train.py script, because it can handle the type of data better.")
"""