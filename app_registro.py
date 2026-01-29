import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Pre-Registro Casino TAM", page_icon="🎟️")

# CONEXIÓN CON GOOGLE SHEETS
# Nota: Streamlit usará el link que pusiste en 'secrets' o la URL directa
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def cargar_maestra():
    # Lee la pestaña donde están los números de socio (Hoja1)
    return conn.read(worksheet="Hoja1")

def enmascarar_nombre(nombre):
    palabras = str(nombre).split()
    enmascarado = " ".join([p[0] + "*"*3 for p in palabras if len(p) > 0])
    return enmascarado

# INTERFAZ
st.title("🛡️ Sistema de Pre-Registro")
st.subheader("Casino TAM")

df_maestra = cargar_maestra()

# Formulario de Validación
n_socio_input = st.number_input("Ingrese su Número de Socio:", min_value=1, step=1, value=None)

if n_socio_input:
    # Buscar socio en la columna 'n_socio'
    socio_info = df_maestra[df_maestra['n_socio'] == n_socio_input]
    
    if not socio_info.empty:
        nombre_real = socio_info.iloc[0]['nombre_completo']
        # Limpieza de puntos finales
        nombre_real = nombre_real.rstrip(". ")
        nombre_visible = enmascarar_nombre(nombre_real)
        
        st.success(f"✅ Socio encontrado")
        st.info(f"**Confirmación de identidad:**\n\n¿Es usted: **{nombre_visible}**?")
        
        confirmar = st.checkbox("Sí, soy yo")
        
        if confirmar:
            st.divider()
            with st.form("form_registro"):
                st.write("### Datos de Asistencia")
                telefono = st.text_input("Teléfono de contacto (10 dígitos):")
                cantidad = st.slider("¿Cuántos boletos totales requiere?", 1, 10, 1)
                comentarios = st.text_area("Invitados o notas adicionales:")
                
                boton_finalizar = st.form_submit_button("Confirmar Pre-Registro")
                
                if boton_finalizar:
                    if not telefono:
                        st.error("Por favor ingrese un teléfono.")
                    else:
                        # Crear el nuevo registro
                        nuevo_dato = pd.DataFrame([{
                            "n_socio": n_socio_input,
                            "telefono": telefono,
                            "boletos": cantidad,
                            "comentarios": comentarios,
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }])
                        
                        # LEER datos actuales de la pestaña 'Registros'
                        df_registros = conn.read(worksheet="Registros")
                        
                        # CONCATENAR y GUARDAR
                        df_actualizado = pd.concat([df_registros, nuevo_dato], ignore_index=True)
                        conn.update(worksheet="Registros", data=df_actualizado)
                        
                        st.balloons()
                        st.success(f"¡Registro Exitoso! Su código es: PR-{n_socio_input}")
                        st.info("Tome una captura de pantalla y preséntela el martes.")
    else:
        st.error("❌ El número de socio no existe. Verifique su credencial.")
