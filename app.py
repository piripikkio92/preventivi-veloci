import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configurazione della pagina
st.set_page_config(page_title="Preventivatore Lamiere & Zanzariere", page_icon="📐", layout="wide")

# Titolo e Menu Navigazione
st.title("🛠️ Preventivatore Officina")
st.caption("Calcolo automatico sviluppo, peso e prezzo per lamiere piegate")

modulo = st.sidebar.radio("Seleziona Modulo:", ["📐 Lamiere Piegate (da Foto)", "🦟 Zanzariere (In Arrivo)"])

if modulo == "🦟 Zanzariere (In Arrivo)":
    st.info("ℹ️ Il modulo **Zanzariere** sarà disponibile a breve con il calcolo dei profili, reti e minimi fatturabili.")
else:
    st.header("📸 Preventivo Lamiere Piegate da Foto")
    st.write("Carica una o più foto degli schizzi con le misure.")

    # Upload file
    uploaded_files = st.file_uploader("Carica le foto dei disegni (anche multiple)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        st.subheader("📋 Dettaglio Foto Caricate")
        
        totale_pezzi = 0
        totale_peso = 0.0
        totale_prezzo = 0.0

        for index, file in enumerate(uploaded_files):
            # Correggiamo il parametro per evitare l'errore
            st.image(file, caption=f"Foto {index+1}: {file.name}", use_container_width=True)

        st.divider()
        st.subheader("📊 RIEPILOGO TOTALE PREVENTIVO")
        col1, col2, col3 = st.columns(3)
        col1.metric("Pezzi Totali", f"{totale_pezzi} PZ")
        col2.metric("Peso Complessivo", f"{totale_peso:.2f} kg")
        col3.metric("Prezzo Totale", f"{totale_prezzo:.2f} €")
        
        # Pulsante per invio rapido
        st.button("📲 Invia Preventivo")
