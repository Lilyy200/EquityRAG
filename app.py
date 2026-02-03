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
    # Récupération du nom du document pour l'affichage
    current_doc_name = st.session_state.get('current_doc', 'Document')
    st.subheader(f"📊 Analyse active : {current_doc_name}")

    # --- NOUVEAU : DASHBOARD EXÉCUTIF ---
    with st.container():
        col_summary, col_download = st.columns([3, 1])
        
        with col_summary:
            st.markdown("#### ✨ Synthèse Stratégique")
        
        if st.button("🚀 Générer le résumé exécutif automatique"):
            with st.spinner("Analyse approfondie en cours..."):
                # Appel de la fonction de synthèse dans l'engine
                summary_res = st.session_state.engine.generate_executive_summary(st.session_state.vectors)
                
                # Affichage du résumé
                st.markdown("""---""")
                st.markdown(summary_res["answer"])
                
                # Bouton de téléchargement
                st.download_button(
                    label="📥 Télécharger l'analyse (TXT)",
                    data=summary_res["answer"],
                    file_name=f"Analyse_{current_doc_name}.txt",
                    mime="text/plain"
                )
                st.markdown("""---""")

    # --- ZONE DE CHAT LIBRE ---
    st.markdown("#### 💬 Assistant Expert")
    user_input = st.text_input("Pose une question spécifique sur les chiffres, les risques ou la stratégie :")
    
    if user_input:
        with st.spinner("L'IA parcourt le rapport financier..."):
            # On utilise la fonction get_response de ton engine
            response = st.session_state.engine.get_response(user_input, st.session_state.vectors)
            
            # Affichage de la réponse
            st.markdown("### 📝 Réponse de l'Analyste :")
            st.info(response["answer"])
            
            # Affichage des sources (traçabilité)
            with st.expander("🔍 Sources consultées dans le document"):
                for i, doc in enumerate(response["context"]):
                    # On affiche la page si elle est présente dans les métadonnées de PyMuPDF
                    page_num = doc.metadata.get('page', 'N/A')
                    # Si c'est un index, on ajoute +1 car PyMuPDF commence à 0
                    if isinstance(page_num, int): page_num += 1
                    
                    st.markdown(f"**Extrait {i+1} (Page {page_num}) :**")
                    st.caption(doc.page_content)
                    st.divider()
else:
    st.info("👋 Bienvenue ! Veuillez uploader ou sélectionner un rapport financier dans la barre latérale pour commencer l'analyse.")