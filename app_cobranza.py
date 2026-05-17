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
              # --- CAMBIO PARA CONEXIÓN PÚBLICA (MÁS RÁPIDA) ---
try:
    # Cambia 'TU_ID_AQUÍ' por el código largo de tu link de Excel
    url_maestra = "https://docs.google.com/spreadsheets/d/1OTJz2BFZhY7HypYTaoyqeg_i5ayRGTMQGOOn80RUcJQ/edit?gid=0#gid=0/export?format=csv"
    
    # 2. Lee los datos directamente con Pandas (esto no falla)
    df_m = pd.read_csv(url_maestra)
    
    # ... el resto de tu lógica para buscar el PIN
except Exception as e:
    st.error("Error crítico de acceso. Asegúrate de que el Excel esté en 'Cualquier persona con el enlace'.")
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
