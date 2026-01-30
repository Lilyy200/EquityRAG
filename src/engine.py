import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_community.document_loaders import PyMuPDFLoader  # Optimisé par rapport à PyPDF

class FinancialEngine:
    def __init__(self):
        # Embeddings gratuits exécutés localement sur ton CPU
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # LLM performant et gratuit via l'API Groq
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    def process_pdf(self, file_path):
        """
        Charge le PDF avec PyMuPDF pour une meilleure gestion des tableaux 
        et crée le store vectoriel FAISS.
        """
        # Utilisation de PyMuPDFLoader pour la rapidité et la structure
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        
        # Découpage intelligent du texte
        # On garde 1000 caractères avec un overlap pour ne pas perdre le contexte financier
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "]
        )
        final_documents = text_splitter.split_documents(docs)
        
        # Création de l'index FAISS (base de données vectorielle locale)
        vectors = FAISS.from_documents(final_documents, self.embeddings)
        return vectors

    def get_response(self, user_input, vectors):
        """
        Exécute la chaîne RAG : 
        1. Récupère les passages pertinents (Retriever)
        2. Envoie au LLM avec le prompt expert (Generator)
        """
        from src.prompts import FINANCIAL_PROMPT
        
        # Création de la chaîne de documents (RAG Moderne LCEL)
        document_chain = create_stuff_documents_chain(self.llm, FINANCIAL_PROMPT)
        
        # Configuration du retriever (top 3 passages les plus proches)
        retriever = vectors.as_retriever(search_kwargs={"k": 3})
        
        # Chaîne finale
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # Invocation
        response = retrieval_chain.invoke({"input": user_input})
        return response