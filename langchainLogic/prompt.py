import os
import re

from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

from langchainLogic.indexer import indexRepo
from .retriever import CustomRetriever, deeplake_simsearch


def promptLangchain(repoURL, promptBody, tags, related_files, type):
    print("Starting promptLangchain function...")
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())

    print("Indexing repository...")

    # check if repo is already indexed
    ds_path = ""
    if os.path.exists("vectordbs/" + repoURL.split("/")[-1]):
        ds_path = "vectordbs/" + repoURL.split("/")[-1]
        print("repo already indexed")


    else:
        print("repo not indexed yet")
        ds_path = indexRepo(repoURL)

    print("Create Context...")

    # Suche nach relevanten Dokumenten im DeepLake basierend auf dem gegebenen Issue
    issue_documents = deeplake_simsearch(OpenAIEmbeddings(disallowed_special=()), ds_path, promptBody, 5)

    # Extrahiere die 'source'-Metadaten aus den gefundenen Dokumenten
    issue_retrieved_sources = [doc.metadata['source'] for doc in issue_documents]

    # Entferne doppelte 'source'-Einträge, um eine eindeutige Liste zu erhalten
    unique_issue_sources = list(set(issue_retrieved_sources))

    # Kombiniere die eindeutigen 'source'-Einträge mit den zusätzlichen Dateien, wobei Dopplungen vermieden werden
    merged_sources = set(unique_issue_sources).union(set(related_files))

    # Konvertiere das Set wieder in eine Liste
    final_source_list = list(merged_sources)

    print("Configuring retriever...")
    retriever, context = CustomRetriever(final_source_list, ds_path)
    print("loaded retriever")

    print("Loading chat model...")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    model = ChatOpenAI(model="gpt-4", temperature=0.3)

    print("Preparing questions and initialize Conversation...")
    questions = []
    if type == "retriever":
        qa = ConversationalRetrievalChain.from_llm(
            model, retriever=retriever, memory=memory, verbose=False)  # add verbose = True to see the full convo

        if len(related_files) > 0:
            questions.append("What are the files" + str(related_files) + " about?")

        base_questions = [
            f"""Resolve the issue in the given text the best way you are able to, which is delimited by XML tags. Only print the Source code as answer. The issue is enclosed within: <Issue> "
              {promptBody}
              </Issue>
              Relevant information for the following questions is provided in the tags: {tags}""",
            "In which class should the previously generated code be placed?",
            'What are these code about and which files you can see?'
        ]
        questions.extend(base_questions)
        print("Starting conversation...")
        chat_history = []

        for question in questions:
            results = qa({"question": question, "chat_history": chat_history})
            print(f"-> **Question**: {question} \n")
            print(f"**Answer**: {results['answer']} \n")
            result = results["answer"]

    if type == "context":
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
        Try to resolve the issue in the given text with the given code in the best way you are able to. 
        Edit the existing code and also use the functions and methods that are already in use, unless you need to develop new ones
        Only provide the Source code as answer:
        
        {text}
        """
        )
        inputs = {
            "text": promptBody + '\n' + str(context)
        }

        chain = LLMChain(llm=model, memory=memory, prompt=prompt_template, verbose=True)
        result = chain.run(inputs)

    print(result)
    print("Appending result to text file...")

    # save result to text file with reponame
    repo_name = repoURL.split("/")[-1]

    with open("result/result_" + repo_name + ".txt", "a") as myfile:
        myfile.write(result + "\n")
        myfile.close()

    # Extract only the code from the result
    extracted_code = extract_code_from_text(result)

    # Save the extracted code to a text file
    with open("result/result_" + repo_name + ".txt", "a") as myfile:
        myfile.write(extracted_code + "\n")
        myfile.close()

    print("promptLangchain function completed.")


def extract_code_from_text(text):
    pattern = r"’’’python(.*?)’’’"
    matches = re.findall(pattern, text, re.DOTALL)
    code_only = '\n'.join(matches)
    return code_only
