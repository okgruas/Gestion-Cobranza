import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL NEÓN RS
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, b, span, label { color: #00FF00 !important; }
    .stTextInput>div>div>input { background-color: #111; color: #00FF00; border: 1px solid #00FF00; }
    .stButton>button { background-color: #00FF00; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE SEGURIDAD
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin = st.text_input("Introduce PIN", type="password")
        if st.button("Ingresar"):
            if pin == "2026":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ PIN incorrecto")
else:
    st.title("💸 ¡CONEXIÓN EXITOSA!")
    st.write("Si ves esto, el diseño y el PIN están perfectos.")
    st.write("El problema está en los Secrets de Google Sheets.")
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
