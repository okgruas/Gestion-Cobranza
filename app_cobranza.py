import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. CONFIGURACIÓN VISUAL NEÓN RS
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, b, span, label { color: #00FF00 !important; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111; color: #00FF00; border: 1px solid #00FF00;
    }
    .stButton>button {
        background-color: #00FF00; color: black; font-weight: bold; width: 100%;
        border-radius: 10px; height: 50px;
    }
    .stSidebar { background-color: #111; }
    /* Estilo para el botón de WhatsApp */
    .btn-whatsapp {
        background-color: #00FF00; color: black; padding: 10px; 
        border-radius: 5px; text-align: center; font-weight: bold; 
        text-decoration: none; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE SEGURIDAD (PIN 2026)
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Acceso")
            pin = st.text_input("Introduce PIN de acceso", type="password")
            if st.button("Ingresar"):
                if pin == "2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
        return False
    return True

# 3. EJECUCIÓN PRINCIPAL
if verificar_acceso():
    # LA CONEXIÓN OCURRE AQUÍ ADENTRO PARA EVITAR PANTALLA NEGRA AL INICIO
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("Error de conexión: Revisa tus Secrets en Streamlit Cloud.")
        st.stop()

    st.sidebar.title("MENU COBRANZA")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    menu = st.sidebar.selectbox("Opciones:", ["Panel de Cobranza", "Nuevo Registro"])

    # --- MÓDULO: PANEL DE COBRANZA ---
    if menu == "Panel de Cobranza":
        st.title("💸 Gestión de Cobranza Directa")
        try:
            df = conn.read()
            if df is not None and not df.empty:
                # Limpiar nombres de columnas
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                for idx, row in df.iterrows():
                    nombre = str(row.get('nombre', 'Sin nombre'))
                    if nombre.lower() != "nan" and nombre.strip() != "":
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"👤 **Cliente:** {nombre}")
                                st.markdown(f"💰 **Monto:** ${row.get('monto', 0)}")
                            with c2:
                                # Link dinámico de WhatsApp
                                tel = str(row.get('teléfono', '')).replace(" ", "").split('.')[0]
                                msg = f"Hola *{nombre}*, recordatorio de pago pendiente de Cobranza App. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 Cobrar</a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No hay registros en la base de datos de Google Sheets.")
        except Exception as e:
            st.error(f"No se pudieron leer los datos. Revisa la URL del Excel en Secrets. Error: {e}")

    # --- MÓDULO: REGISTRO ---
    elif menu == "Nuevo Registro":
        st.title("📝 Registrar en la Nube")
        with st.form("registro_nube"):
            nombre_nuevo = st.text_input("Nombre Completo del Cliente")
            monto_nuevo = st.number_input("Monto del Préstamo", min_value=0)
            tel_nuevo = st.text_input("Teléfono (10 dígitos)")
            
            st.markdown("### 👥 Avales")
            col1, col2 = st.columns(2)
            with col1:
                aval1 = st.text_input("Nombre Aval 1")
                tel_aval1 = st.text_input("Teléfono Aval 1")
            with col2:
                aval2 = st.text_input("Nombre Aval 2")
                tel_aval2 = st.text_input("Teléfono Aval 2")
            
            if st.form_submit_button("💾 GUARDAR EN GOOGLE SHEETS"):
                if nombre_nuevo and tel_nuevo:
                    try:
                        df_actual = conn.read()
                        nuevo = pd.DataFrame([{
                            "fecha": datetime.now().strftime("%d/%m/%Y"),
                            "nombre": nombre_nuevo,
                            "monto": monto_nuevo,
                            "teléfono": tel_nuevo,
                            "aval_1": aval1,
                            "tel_aval_1": tel_aval1,
                            "aval_2": aval2,
                            "tel_aval_2": tel_aval2
                        }])
                        df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                        conn.update(data=df_final)
                        st.success(f"✅ ¡{nombre_nuevo} guardado con éxito!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.warning("El nombre y teléfono son obligatorios.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
