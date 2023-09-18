from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from dotenv import load_dotenv
import os
from langchain.chains.retrieval_qa.base import BaseRetriever
from pydantic import BaseModel, Field

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")


class MyRetriever(BaseRetriever, BaseModel):
    docs: list = Field(default_factory=list)

    def __init__(self, docs=None, **kwargs):
        super().__init__(**kwargs)
        if docs:
            self.docs = self.process_docs(docs)

    def process_docs(self, docs):
        essential_docs = [doc for doc in docs if doc.metadata['file_name'] == 'train.py']
        return sorted(essential_docs, key=lambda x: x.metadata['chunk_id'])

    def _get_relevant_documents(self, query):
        return self.docs

def CustomRetriever(files):
    # Laden Sie den VectorIndex mit den hochgeladenen Chunks
    dataset_path = "../vectordbs/chatbot_doc"
    embeddings = OpenAIEmbeddings(disallowed_special=())
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding=embeddings)
    docs = (db.similarity_search(query=" ", k=10000000))

    retriever = MyRetriever(docs=docs)
    return retriever


model = ChatOpenAI(model="gpt-4")
retriever = CustomRetriever(['train.py'])
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever, memory=memory, verbose=True)
res = qa.run(
    """
    a CNN should be used instead of the BERT model in the train.py script, because it can handle the type of data better.
The CNN should not be too complex, but also not too simple and should be generated using Tensorflow. 
The CNN should be integrated into the logic and adapted according to the word vectors used. Change the code of it, as good as you can.

"""
)
print(res)





