import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# --- FUNCIÓN DE ACCESO (RENTAS) ---
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
                    # USAMOS EL LINK DIRECTO PARA EVITAR ERRORES DE SECRETS
                    url_maestra = "1OTJz2BFZhY7HypYTaoyqeg_i5ayRGTMQGOOn80RUcJQ/edit?gid=0#gid=0"
                    conn_m = st.connection("gsheets", type=GSheetsConnection, spreadsheet=url_maestra)
                    df_m = conn_m.read(ttl=0)
                    
                    match = df_m[df_m['pin'].astype(str) == pin_usuario]
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("PIN incorrecto")
                except Exception as e:
                    st.error("Error de conexión. Revisa que el Excel esté compartido con el correo de la app.")
        return False
    return True

# 2. EJECUCIÓN
if verificar_acceso():
    st.sidebar.success(f"Bienvenido: {st.session_state['nombre_cliente']}")
    # Conexión al Excel del cliente que entró
    try:
        conn = st.connection("gsheets", type=GSheetsConnection, spreadsheet=st.session_state["url_cliente"])
        df = conn.read(ttl=0)
        st.title("📊 Panel de Cobranza")
        st.dataframe(df)
    except:
        st.error("No se pudo cargar el Excel del cliente.")
