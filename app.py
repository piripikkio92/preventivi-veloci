import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Preventivatore Lamiere & Zanzariere", page_icon="📐", layout="wide")

# Configurazione della chiave API di Google Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Chiave API Gemini non trovata nei Secrets di Streamlit!")

# Database materiali di base (finitura, spessore, peso specifico kg/m2, prezzo €/kg)
DATABASE_MATERIALI = {
    "RAL 8017": {"spessore": 1.2, "peso_spec": 3.55, "prezzo_kg": 11.50},
    "MARRONE 8017": {"spessore": 1.2, "peso_spec": 3.55, "prezzo_kg": 11.50},
    "RAL 9010": {"spessore": 1.2, "peso_spec": 3.55, "prezzo_kg": 11.00},
    "BIANCO 9010": {"spessore": 1.2, "peso_spec": 3.55, "prezzo_kg": 11.00},
    "ZINCATA": {"spessore": 1.5, "peso_spec": 12.00, "prezzo_kg": 3.20},
}

st.title("🛠️ Preventivatore Officina")
st.caption("Calcolo automatico sviluppo, peso e prezzo per lamiere piegate")

modulo = st.sidebar.radio("Seleziona Modulo:", ["📐 Lamiere Piegate (da Foto)", "🦟 Zanzariere (In Arrivo)"])

if modulo == "🦟 Zanzariere (In Arrivo)":
    st.info("ℹ️ Il modulo **Zanzariere** sarà disponibile a breve con il calcolo dei profili, reti e minimi fatturabili.")
else:
    st.header("📸 Preventivo Lamiere Piegate da Foto")
    st.write("Carica una o più foto degli schizzi con le misure.")

    uploaded_files = st.file_uploader("Carica le foto dei disegni (anche multiple)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        st.subheader("📋 Dettaglio Foto ed Estrazione Dati")
        
        totale_pezzi = 0
        totale_peso = 0.0
        totale_prezzo = 0.0

        # Modello aggiornato a gemini-3.8-flash
        model = genai.GenerativeModel('gemini-3.8-flash')

        for index, file in enumerate(uploaded_files):
            col_img, col_data = st.columns([1, 1])
            
            image = Image.open(file)
            col_img.image(image, caption=f"Foto {index+1}: {file.name}", use_container_width=True)

            with col_data:
                st.write(f"🔍 **Analisi IA per Foto {index+1}:**")
                
                prompt = """
                Analizza lo schizzo tecnico di lamiere piegate nella foto ed estrai per ogni pezzo:
                1. I lati in mm (es. [50, 100, 100])
                2. L'altezza/lunghezza H in mm (es. 1000)
                3. La quantità di pezzi (es. 1)
                4. Il colore/materiale (es. "RAL 8017" o "RAL 9010")

                Rispondi ESCLUSIVAMENTE in formato JSON con la seguente struttura:
                [
                  {
                    "lati": [50, 100, 100],
                    "H": 1000,
                    "quantita": 1,
                    "colore": "RAL 8017"
                  }
                ]
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    text_response = response.text
                    
                    json_match = re.search(r'\[.*\]', text_response, re.DOTALL)
                    if json_match:
                        pezzi_letti = json.loads(json_match.group(0))
                        
                        for p_idx, pezzo in enumerate(pezzi_letti):
                            lati = pezzo.get("lati", [])
                            H = pezzo.get("H", 1000)
                            qty = pezzo.get("quantita", 1)
                            colore = pezzo.get("colore", "RAL 8017").upper()
                            
                            sviluppo_mm = sum(lati)
                            sviluppo_m = sviluppo_mm / 1000.0
                            H_m = H / 1000.0
                            
                            mat_info = DATABASE_MATERIALI.get(colore, DATABASE_MATERIALI["RAL 8017"])
                            peso_spec = mat_info["peso_spec"]
                            prezzo_kg = mat_info["prezzo_kg"]
                            
                            area_singola = sviluppo_m * H_m
                            peso_singolo = area_singola * peso_spec
                            prezzo_singolo = peso_singolo * prezzo_kg
                            
                            peso_tot_pezzo = peso_singolo * qty
                            prezzo_tot_pezzo = prezzo_singolo * qty
                            
                            totale_pezzi += qty
                            totale_peso += peso_tot_pezzo
                            totale_prezzo += prezzo_tot_pezzo
                            
                            st.markdown(f"**Pezzo {p_idx+1} ({colore}):**")
                            st.write(f"• Quote: {lati} mm | H: {H} mm | Qtà: {qty} pz")
                            st.write(f"• Sviluppo: **{sviluppo_mm} mm** | Peso: **{peso_tot_pezzo:.2f} kg** | Prezzo: **{prezzo_tot_pezzo:.2f} €**")
                    else:
                        st.warning("Non è stato possibile identificare chiaramente i dati nella foto. Verifica la leggibilità.")
                except Exception as e:
                    st.error(f"Errore durante l'elaborazione dell'immagine: {e}")

        st.divider()
        st.subheader("📊 RIEPILOGO TOTALE PREVENTIVO")
        col1, col2, col3 = st.columns(3)
        col1.metric("Pezzi Totali", f"{totale_pezzi} PZ")
        col2.metric("Peso Complessivo", f"{totale_peso:.2f} kg")
        col3.metric("Prezzo Totale", f"{totale_prezzo:.2f} €")
        
        st.button("📲 Invia Preventivo")
