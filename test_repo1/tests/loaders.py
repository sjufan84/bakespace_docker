# %%
from pathlib import Path
root_dir = Path('../../streamlined_wireframes/')
import os
## Creating a language chain that can help take a github repo and other documentation and create a language chain that can reference those documents when needed.
from langchain.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    Language,
)
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import openai
load_dotenv()
import streamlit as st

# Get OpenAI and Pinecone API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_KEY")
openai.organization = os.getenv("OPENAI_ORG")
pinecone_env = os.getenv("PINECONE_ENV")

# Initialize Pinecone
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)





# %%
from git import Repo

# Create an empty list for the root directories
root_dirs = []

# Let the user select the type of loader they want to use
# For now we will start with a git repo loader and pdf loader
def clone_git_repo(urls):
   
    # Set the urls for the repos 
    urls = [
        "https://github.com/hwchase17/langchain",
        "https://github.com/streamlit/streamlit",
    ]   

    for i, url in enumerate(urls):
        repo = Repo.clone_from(url, to_path=f"./example_data{i}/test_repo1")
        # Add the root directory to the list
        root_dirs.append(f"./example_data{i}/test_repo1")
        branch = repo.head.reference
        print(branch.name)

    # Return the root directories
    return root_dirs


# Define a function to load and split the text from the repos
def load_and_split_text(root_dir):

    # Create an empty list for the docs 
    docs = []

    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size = 1000, chunk_overlap = 15
    )
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".py") and "/.venv/" not in dirpath:
                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding="utf-8")
                    docs.extend(loader.load_and_split(text_splitter=python_splitter))
                except Exception as e:
                    pass
    st.write((f"{len(docs)}"))

    # Return the docs
    return docs


# Create the embeddings object
embeddings = OpenAIEmbeddings(
    openai_api_key = openai.api_key,
    openai_organization= openai.organization
)


from langchain.document_loaders import PyPDFLoader
# Create a function to load and split the text from a pdf
def load_and_split_pdf(file_paths):
    # Create an uploader for the pdf(s)
    file_paths = st.file_uploader("Upload a PDF", accept_multiple_files=True)
    docs = []
    for file_path in file_paths:
        pdf_loader = PyPDFLoader(file_path=file_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000, chunk_overlap = 15
        )
        docs.extend(pdf_loader.load_and_split(text_splitter=text_splitter))
    st.write((f"{len(docs)}"))

    # Return the docs
    return docs
    
# Define a function to connnect to pinecone and create a vector store
def create_vector_store():
    # Create a vector store
    root_dir = "./example_data0/test_repo1"
    # Connect to the Pinecone vector store
    index = pinecone.GRPCIndex(index_name=index_name, dimension=embeddings.dimension)
    docs = load_and_split_text(root_dir)
    source_name = "langchain"
    for i, doc in enumerate(docs):
        metadata = {
            "id": f'{source_name}_{i}',
            "type": type,
            "repo": repo
        }
        doc.metadata["id"] = f'{source_name}_{i}'
        doc.metadata['type'] = type
        doc.metadata['repo'] = repo
        

        # Create a list of the texts from the docs
        texts = []
        for doc in docs:
            texts.append(doc.page_content)

        # Create the vectors from the texts
        vectors=embeddings.embed_documents(texts)

        # Create a new dataframe from the doc data
        import pandas as pd

        # Set the columns to "text", "id", "metadata"
        df = pd.DataFrame(columns=["values", "id", "metadata", "text"])

        # Loop through the docs and set the values for each column
        for i, doc in enumerate(docs):
            df = df.append(
                {
                    "values": vectors[i],
                    "id": doc.metadata["id"],
                    "metadata": doc.metadata,
                    "text": doc.page_content
                },
                ignore_index=True,
            )

        index.upsert_from_dataframe(df, batch_size=50)

        # %%
        st.write(index.describe_index_stats())



