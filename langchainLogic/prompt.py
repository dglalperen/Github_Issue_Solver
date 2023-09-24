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
from utils.patch_processor import process_result_txt, replace_file_content
from .retriever import CustomRetriever, deeplake_simsearch


def extract_code_from_text(text):
    pattern = r'```(?:\w+)?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    code_only = '\n'.join(matches)
    return code_only


def promptLangchain(repoURL, promptBody, tags, related_files, type):
    print("Starting promptLangchain function...")
    load_dotenv()
    vectordbsfolder = "vectordbs/"
    os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(disallowed_special=())

    print("Indexing repository...")

    # check if repo is already indexed
    ds_path = ""
    if os.path.exists(vectordbsfolder + repoURL.split("/")[-1]):
        ds_path = vectordbsfolder + repoURL.split("/")[-1]
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
    final_source_list = list(set(list(merged_sources)))

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
        text = """
Try to solve the issue in the given text as best you can with the given code. 
Edit the existing code and also use the functions and methods already used, unless you need to develop new ones. It is also very important that you keep imports from other files in the project. 
Your output should show the whole file without truncations when modifying a file, even if changes are made in multiple files. 
Please make sure you add a JSON object at the end in the following format:

{
    'source': '<source>'
}

Where 'source' is the source from the metadata of the original file. 
                """

        prompt_template = PromptTemplate(
            input_variables=["text"],
            template='{text}'
        )


        chain = LLMChain(llm=model, memory=memory, prompt=prompt_template, verbose=False)
        result = chain.run(text=text + '\n' + promptBody + '\n' + str(context))

    print(result)
    print("Appending result to text file...")

    # save result to text file with reponame
    repo_name = repoURL.split("/")[-1]


    # Extract only the code from the result
    extracted_code = extract_code_from_text(result)

    # Save the extracted code to a text file
    with open("result/result_" + repo_name + ".txt", "a") as myfile:
        myfile.write(extracted_code + "\n")
        myfile.close()


    code_json_pair = process_result_txt("result/result_" + repo_name + ".txt")

    for pair in code_json_pair:
        replace_file_content(pair['json']['source'], pair['code'])
    print("promptLangchain function completed.")



