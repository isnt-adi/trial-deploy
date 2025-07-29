import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from backend.syst_instructions import QA_PROMPT

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

# --- LLM Setup ---
def load_llm():
    pipe = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        tokenizer="google/flan-t5-base",
        device=-1,
        max_new_tokens=512
    )
    return HuggingFacePipeline(pipeline=pipe)

llm = load_llm()

# --- PDF Text Extraction ---
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- QA Chain Initialization ---
def initialize_qa_chain(uploaded_file):
    raw_text = extract_text_from_pdf(uploaded_file)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(raw_text)

    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_texts(chunks, embedding=embedder)

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=False,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )
    return qa_chain
