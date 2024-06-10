from langchain_community.document_loaders import PyPDFLoader, OnlinePDFLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import Pinecone as PC

import os

def main():
    loader = UnstructuredExcelLoader("/home/niks/Downloads/report1709795410593.xlsx")
    data = loader.load()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
    docs=text_splitter.split_documents(data)
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '79e661c4-df40-4cbe-b886-3ce2bcd49ac2')
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    index_name = "perfconfhack"
    os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
    docsearch=PC.from_texts([t.page_content for t in docs], embeddings, index_name=index_name)

if __name__ == "__main__":
    main()
[9:48 AM] from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import Pinecone as PC
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
import os, requests

def format_llama_prompt(user_prompt):
    prompt = """\
<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible.  Your answers should not include any harmful, offensive, dangerous, or illegal content.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please ask for more details.
<</SYS>>

{user_prompt}[/INST]\
"""
    return prompt.format(user_prompt=user_prompt)

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
def main():
    query = input("Enter your query to search: ")
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '79e661c4-df40-4cbe-b886-3ce2bcd49ac2')
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    index_name = "perfconfhack"
    os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
    docsearch=PC.from_existing_index(index_name, embeddings)
    docs=docsearch.similarity_search(query, k=10)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt_RAG = prompt_template.format(context=docs, question=query)


    URL = "https://llama-2-7b-chat-perfconf-hackathon.apps.dripberg-dgx2.rdu3.labs.perfscale.redhat.com"

    endpoint = "/generate"

    headers = {
        "Content-Type": "application/json"
    }

    prompt = format_llama_prompt(prompt_RAG)

    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.9,  # Just anSho example
            "repetition_penalty": 1.03,  # Just an example
            "details": False
        }
    }

    response = requests.post(f"{URL}{endpoint}", headers=headers, json=data, verify=False)  # , stream=True)
    print(response.json().get("generated_text"))

if __name__ == "__main__":
    main()