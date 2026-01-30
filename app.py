import streamlit as st
import os
from src.engine import FinancialEngine
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Equity Research", layout="wide")
st.title("📊 AI Financial Report Analyzer")

# Initialisation du moteur
if "engine" not in st.session_state:
    st.session_state.engine = FinancialEngine()

# Barre latérale pour l'upload
with st.sidebar:
    st.header("Upload")
    uploaded_file = st.file_uploader("Rapport financier (PDF)", type="pdf")
    
    if uploaded_file and "vectors" not in st.session_state:
        if st.button("Lancer l'indexation"):
            with st.spinner("Analyse du rapport..."):
                # Sauvegarde tempo pour le loader
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.vectors = st.session_state.engine.process_pdf("temp.pdf")
                st.success("Rapport prêt pour analyse !")

# Zone de chat
if "vectors" in st.session_state:
    user_input = st.text_input("Pose une question sur les résultats, les risques ou la stratégie :")
    
    if user_input:
        with st.spinner("L'IA analyse les chiffres..."):
            response = st.session_state.engine.get_response(user_input, st.session_state.vectors)
            st.markdown(f"### Réponse de l'Analyste :\n {response['answer']}")
            
            with st.expander("Sources consultées dans le document"):
                st.write(response["context"])
else:
    st.info("Veuillez uploader un rapport financier dans la barre latérale pour commencer.")