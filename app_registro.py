import streamlit as st
import sqlite3
import os
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pre-Registro Casino TAM",
    page_icon="♣️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DB_NAME = 'evento_casino_v6.db'
LOGO_PATH = "logo.png"

# --- 2. ESTILO VISUAL PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    /* Estilo para botones grandes y legibles en móvil */
    .stButton>button {
        width: 100%;
        height: 3.5em;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 12px;
        background-color: #ff4b4b;
        color: white;
    }
    /* Inputs con bordes más redondeados */
    div[data-baseweb="input"] {
        border-radius: 10px !important;
    }
    /* Estilo de la tabla de precios */
    .precio-tabla {
        font-size: 14px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES AUXILIARES ---
def cargar_logo():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def guardar_prerregistro(n_socio, nombre, acompanantes, invitados):
    try:
        with sqlite3.connect(DB_NAME, timeout=30) as conn:
            cursor = conn.cursor()
            # Crear la tabla si no existe por seguridad
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registros_completos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turno TEXT,
                    n_socio TEXT,
                    nombre TEXT,
                    acompanantes TEXT,
                    invitados TEXT,
                    estatus TEXT,
                    total REAL,
                    desglose_boletos TEXT
                )
            """)
            
            # Obtener último ID para el turno
            res = cursor.execute("SELECT id FROM registros_completos ORDER BY id DESC LIMIT 1").fetchone()
            proximo_id = (res[0] + 1) if res else 1
            nuevo_turno = f"PRE-{str(proximo_id).zfill(3)}"
            
            cursor.execute("""
                INSERT INTO registros_completos (turno, n_socio, nombre, acompanantes, invitados, estatus, total, desglose_boletos) 
                VALUES (?,?,?,?,?,?,?,?)""", 
                (nuevo_turno, n_socio, nombre.upper(), acompanantes.upper(), invitados.upper(), 'Pre-Registro', 0.0, 'PENDIENTE'))
            conn.commit()
            return nuevo_turno
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- 4. LÓGICA DE INTERFAZ ---
if 'registrado' not in st.session_state:
    st.session_state.registrado = False

logo_data = cargar_logo()

if not st.session_state.registrado:
    # Encabezado
    if logo_data:
        st.markdown(f'<center><img src="data:image/png;base64,{logo_data}" width="160"></center>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center;'>♣️</h1>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Prerregistro Digital</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Evento Casino TAM</p>", unsafe_allow_html=True)

    with st.form("form_registro"):
        st.subheader("👤 Datos del Titular")
        c1, c2 = st.columns([1, 2])
        n_socio = c1.text_input("N° Socio", placeholder="Ej: 1450")
        nombre = c2.text_input("Nombre Completo", placeholder="JUAN PEREZ GARCIA")
        
        st.write("---")
        st.subheader("👥 Acompañantes")
        
        acompanantes = st.text_area(
            "Socios Acompañantes (Opcional)", 
            placeholder="Ejemplos:\n1. MARIA PEREZ (Socio)\n2. JOSE PEREZ (Socio)",
            help="Escriba un nombre por renglón"
        )
        
        invitados = st.text_area(
            "Invitados No Socios (Opcional)", 
            placeholder="Ejemplos:\n1. LUIS GOMEZ (Invitado)\n2. CARLOS RUIZ (Invitado)"
        )

       # TABLA DE PRECIOS DETALLADA Y CORREGIDA
        with st.expander("💰 CONSULTAR TABLA DE PRECIOS"):
            st.markdown("""
            | Concepto | Precio Socio | Precio Invitado |
            | :--- | :--- | :--- |
            | **Boleto Evento** | $400.00 | $500.00 |
            | **Boleto Disco (Sin Reservado)** | $250.00 | $300.00 |
            | **Boleto Disco (Con Reservado)** | $350.00 | $400.00 |
            """)
            st.info("💡 Nota: Los precios son por persona. La selección final se realiza en el club.")

        st.info("📌 Al finalizar, se generará un número de turno que deberá presentar en el Casino.")
        
        enviar = st.form_submit_button("✅ GENERAR MI TURNO")

        if enviar:
            if n_socio and nombre:
                turno_ok = guardar_prerregistro(n_socio, nombre, acompanantes, invitados)
                if turno_ok:
                    st.session_state.turno = turno_ok
                    st.session_state.nombre_usuario = nombre.upper()
                    st.session_state.registrado = True
                    st.rerun()
            else:
                st.error("⚠️ El número de socio y nombre son obligatorios.")

else:
    # --- PANTALLA DE TICKET FINAL (OPCION DE CAPTURA) ---
    st.balloons()
    st.markdown("---")
    
    # Diseño del Ticket para Celular
    st.markdown(f"""
        <div style="
            background-color: white; 
            padding: 25px; 
            border-radius: 20px; 
            border: 3px solid #ff4b4b; 
            text-align: center;
            max-width: 350px;
            margin: auto;
            color: #333;
        ">
            <h4 style="margin: 0; color: #888;">TURNO DE ATENCIÓN</h4>
            <div style="background-color: #ff4b4b; color: white; border-radius: 15px; margin: 15px 0; padding: 10px;">
                <h1 style="margin: 0; font-size: 50px;">{st.session_state.turno}</h1>
            </div>
            <h3 style="margin: 0;">{st.session_state.nombre_usuario}</h3>
            <hr style="border: 0.5px dashed #ccc;">
            <p style="font-size: 14px; line-height: 1.4;">
                Mencione este número en la recepción del Casino para finalizar su compra y elegir boletos.
            </p>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px;">
                <p style="margin:0; font-weight: bold; font-size: 12px;">📸 TOME UNA CAPTURA DE PANTALLA</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("⬅️ Hacer otro registro"):
        st.session_state.registrado = False
        st.rerun()

# Footer
st.markdown("<br><p style='text-align: center; font-size: 10px; color: gray;'>© 2026 Casino Tampico - Control de Acceso</p>", unsafe_allow_html=True)

