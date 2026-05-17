import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN PARA LEER GOOGLE SHEETS PUBLICADO ---
def leer_publicado(url):
    # Esto limpia el link para que sea un CSV directo
    base = url.split('/edit')[0]
    final_url = f"{base}/export?format=csv"
    return pd.read_csv(final_url)

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN", type="password")
        if st.button("Ingresar"):
            try:
                # USA TU LINK DE LA HOJA CONTROL AQUÍ
                url_control = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
                df_m = leer_publicado(url_control)
                
                # Limpiar columnas
                df_m.columns = df_m.columns.str.strip().lower()
                
                # Buscar PIN
                match = df_m[df_m['pin'].astype(str).str.strip() == pin_usuario.strip()]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                    st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
            except Exception as e:
