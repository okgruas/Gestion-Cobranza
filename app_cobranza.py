import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# --- FUNCIÓN DE ACCESO ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.title("🔐 Acceso")
            pin_usuario = st.text_input("PIN", type="password")
            if st.button("Ingresar"):
                try:
                    # LINK DE TU HOJA MAESTRA (LA VERDE)
                    url_maestra = "https://docs.google.com/spreadsheets/d/TU_ID_AQUÍ/edit"
                    conn_m = st.connection("gsheets", type=GSheetsConnection, spreadsheet=url_maestra)
                    # Aquí pedimos que lea la pestaña llamada 'Control'
                    df_m = conn_m.read(worksheet="Control", ttl=0)
                    
                    match = df_m[df_m['pin'].astype(str) == pin_usuario]
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("PIN incorrecto")
                except Exception as e:
                    st.error("Error de conexión. Revisa el link y los permisos.")
        return False
    return True

# 2. CUERPO DE LA APP
if verificar_acceso():
    st.success(f"Bienvenido: {st.session_state['nombre_cliente']}")
    # Aquí iría el resto de tu código de cobranza...
