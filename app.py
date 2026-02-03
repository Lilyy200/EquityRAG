import streamlit as st
import os
from src.engine import FinancialEngine
from dotenv import load_dotenv

# Configuration des chemins
UPLOAD_DIR = "data/pdfs"
DB_DIR = "data/indices"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

load_dotenv()

st.set_page_config(page_title="AI Equity Research", layout="wide", page_icon="📊")

# --- CSS Custom pour un look plus "Finance Terminal" ---
st.markdown("""
    <style>
    .stAlert { border-left: 5px solid #1E3A8A; }
    .stButton>button { width: 100%; background-color: #1E3A8A; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 AI Financial Report Analyzer")

# Initialisation du moteur dans le state
if "engine" not in st.session_state:
    st.session_state.engine = FinancialEngine()

# --- SIDEBAR : GESTION DE LA BIBLIOTHÈQUE ---
with st.sidebar:
    st.header("📂 Bibliothèque de Rapports")
    
    # 1. Upload de nouveau fichier
    uploaded_file = st.file_uploader("Ajouter un rapport (PDF)", type="pdf")
    
    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        db_path = os.path.join(DB_DIR, uploaded_file.name.replace(".pdf", ""))
        
        if st.button(f"🚀 Indexer {uploaded_file.name}"):
            with st.spinner("Analyse et vectorisation..."):
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # On utilise la méthode de l'engine pour créer et sauvegarder
                st.session_state.vectors = st.session_state.engine.process_pdf(file_path, db_path)
                st.success("Document ajouté à la bibliothèque !")

    st.divider()
    
    # 2. Sélection du document de travail
    existing_docs = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
    
    if existing_docs:
        selected_doc = st.selectbox("Choisir un document à analyser", ["Sélectionner..."] + existing_docs)
        
        if selected_doc != "Sélectionner...":
            db_path = os.path.join(DB_DIR, selected_doc.replace(".pdf", ""))
            
            # Charger l'index si on change de document
            if "current_doc" not in st.session_state or st.session_state.current_doc != selected_doc:
                with st.spinner("Chargement de l'index..."):
                    st.session_state.vectors = st.session_state.engine.load_vector_db(db_path)
                    st.session_state.current_doc = selected_doc
    else:
        st.write("Aucun document en bibliothèque.")

# --- ZONE D'ANALYSE PRINCIPALE ---
if "vectors" in st.session_state:
    st.subheader(f"Analyse active : {st.session_state.get('current_doc', 'Nouveau document')}")
    
    user_input = st.text_input("Pose une question sur les résultats, les risques ou la stratégie :")
    
    if user_input:
        with st.spinner("L'IA parcourt le rapport financier..."):
            # On utilise la fonction get_response de ton engine
            response = st.session_state.engine.get_response(user_input, st.session_state.vectors)
            
            # Affichage de la réponse
            st.markdown("### 📝 Réponse de l'Analyste :")
            st.info(response["answer"])
            
            # Affichage des sources (ce que tu aimais)
            with st.expander("🔍 Sources consultées dans le document"):
                for i, doc in enumerate(response["context"]):
                    st.markdown(f"**Extrait {i+1} (Page {doc.metadata.get('page', 'N/A')}) :**")
                    st.caption(doc.page_content)
                    st.divider()
else:
    st.info("👋 Bienvenue ! Veuillez uploader ou sélectionner un rapport financier dans la barre latérale pour commencer l'analyse.")