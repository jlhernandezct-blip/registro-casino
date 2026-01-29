import streamlit as st
import sqlite3
import os
import base64

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Pre-Registro Casino TAM", layout="wide")

DB_NAME = 'evento_casino_v6.db' 
LOGO_PATH = "logo.png"
logo_base64 = ""

if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

# --- 2. FUNCIONES DE BASE DE DATOS ---
def guardar_prerregistro(n_socio, nombre, acompanantes, invitados):
    try:
        with sqlite3.connect(DB_NAME, timeout=30) as conn:
            cursor = conn.cursor()
            # Generar el ID de turno PRE
            res = cursor.execute("SELECT id FROM registros_completos ORDER BY id DESC LIMIT 1").fetchone()
            pid = (res[0] + 1) if res else 1
            tid = f"PRE-{str(pid).zfill(3)}"
            
            cursor.execute("""
                INSERT INTO registros_completos (turno, n_socio, nombre, acompanantes, invitados, estatus, total, desglose_boletos) 
                VALUES (?,?,?,?,?,?,?,?)""", 
                (tid, n_socio, nombre.upper(), acompanantes.upper(), invitados.upper(), 'Pre-Registro', 0.0, 'POR DEFINIR'))
            conn.commit()
            return tid
    except Exception as e:
        st.error(f"Error en la base de datos: {e}")
        return None

# --- 3. INTERFAZ DE BIENVENIDA / AUTENTICACIÓN ---
if 'registrado' not in st.session_state:
    st.session_state.registrado = False

if not st.session_state.registrado:
    # Encabezado con Logo
    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        if logo_base64:
            st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="150">', unsafe_allow_html=True)
        else:
            st.title("♣️")
    
    with col_tit:
        st.title("Prerregistro en Línea · CASINO TAM")
        st.write("---")

    # Formulario de Prerregistro
    st.info("👋 **Bienvenido.** Ingrese sus datos para agilizar su registro físico en el club.")
    
    with st.form("form_pre", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n_soc = c1.text_input("Número de Socio", placeholder="Ej: 1450")
        nom = c2.text_input("Nombre Completo (Socio Titular)", placeholder="Ej: JUAN PEREZ")
        
        st.write("### Datos de Invitados")
        aco = st.text_area("Socios Acompañantes (Nombres)", placeholder="1. MARIA PEREZ\n2. JOSE PEREZ")
        inv = st.text_area("Invitados No Socios (Nombres)", placeholder="1. LUIS GOMEZ\n2. CARLOS RUIZ")
        
        # Tabla de Precios Informativa (Mismos que tu código fuente)
        with st.expander("Ver Precios de Boletos (Informativo)"):
            st.table({
                "Categoría": ["Boleto Socio", "Boleto Invitado", "Disco (Socio)", "Disco (Invitado)"],
                "Precio": ["$400.00", "$500.00", "$250.00 / $350.00", "$300.00 / $400.00"]
            })

        st.warning("⚠️ Al finalizar, se le asignará un turno. Al llegar al Casino, mencione su turno para seleccionar sus boletos y pagar.")
        
        if st.form_submit_button("✅ GENERAR MI TURNO DE PRERREGISTRO"):
            if n_soc and nom:
                turno = guardar_prerregistro(n_soc, nom, aco, inv)
                if turno:
                    st.session_state.turno = turno
                    st.session_state.nombre_usuario = nom.upper()
                    st.session_state.registrado = True
                    st.rerun()
            else:
                st.error("Por favor llene su número de socio y nombre completo.")

else:
    # PANTALLA DE ÉXITO (Simulando la autenticación con su nombre)
    st.balloons()
    st.markdown("---")
    if logo_base64:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="200"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="text-align:center;">
            <h1>¡LISTO, {st.session_state.nombre_usuario}!</h1>
            <p style="font-size:20px;">Tu trámite de prerregistro se ha completado.</p>
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px dashed #ff4b4b; display:inline-block;">
                <h2 style="margin:0;">TURNO: <span style="color:#ff4b4b;">{st.session_state.turno}</span></h2>
            </div>
            <p style="margin-top:20px;">Presenta este código en la recepción del Casino para elegir tus lugares y realizar el pago.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Hacer otro registro"):
        st.session_state.registrado = False
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("Casino Tampico © 2026 - Sistema de Gestión de Eventos")
