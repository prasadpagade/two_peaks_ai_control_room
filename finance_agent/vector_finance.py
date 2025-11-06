import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain


def build_finance_index(csv_path="finance_agent/financial_data.csv"):
    """Build FAISS vector index from financial data"""
    df = pd.read_csv(csv_path)
    docs = [row.to_json() for _, row in df.iterrows()]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    split_docs = splitter.create_documents(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    return vectorstore


def chat_with_finance(vectorstore, query, chat_history=[]):
    """Chat with the financial data through RAG pipeline"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever())
    result = qa({"question": query, "chat_history": chat_history})
    return result["answer"]