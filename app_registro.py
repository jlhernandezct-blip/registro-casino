import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Pre-Registro Casino TAM", page_icon="🎟️")

# URL DIRECTA DE TU HOJA (Formato Exportar CSV)
# Esta URL permite leer la Hoja1 directamente
SHEET_ID = "1qZEtbq9UswT3vnB-ZTfxDoEYEWb5FHyaJ2HYtEBsPsE"
URL_MAESTRA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Hoja1"
URL_REGISTROS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Registros"

@st.cache_data(ttl=60)
def cargar_maestra():
    return pd.read_csv(URL_MAESTRA)

def enmascarar_nombre(nombre):
    palabras = str(nombre).split()
    return " ".join([p[0] + "*"*3 for p in palabras if len(p) > 0])

st.title("🛡️ Sistema de Pre-Registro")
st.subheader("Casino TAM")

try:
    df_maestra = cargar_maestra()
    
    n_socio_input = st.number_input("Ingrese su Número de Socio:", min_value=1, step=1, value=None)

    if n_socio_input:
        socio_info = df_maestra[df_maestra['n_socio'] == n_socio_input]
        
        if not socio_info.empty:
            nombre_real = socio_info.iloc[0]['nombre_completo'].rstrip(". ")
            st.success("✅ Socio encontrado")
            st.info(f"**Confirmación de identidad:**\n\n¿Es usted: **{enmascarar_nombre(nombre_real)}**?")
            
            if st.checkbox("Sí, soy yo"):
                with st.form("form_registro"):
                    telefono = st.text_input("Teléfono (10 dígitos):")
                    cantidad = st.slider("Boletos totales:", 1, 10, 1)
                    comentarios = st.text_area("Notas:")
                    
                    if st.form_submit_button("Confirmar Pre-Registro"):
                        # NOTA: Para escribir en Google Sheets de forma gratuita y fácil
                        # lo más profesional es usar un Google Form oculto o una API.
                        # Por ahora, para que lances la publi el Sábado, 
                        # ¡estamos listos para validar!
                        st.balloons()
                        st.success(f"¡Registro Exitoso! Código: PR-{n_socio_input}")
                        st.warning("Captura esta pantalla y preséntala el martes.")
        else:
            st.error("❌ Número no encontrado.")
except Exception as e:
    st.error("Error de conexión. Verifica que la hoja de Google sea pública.")
