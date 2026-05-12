import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. ESTILO NEÓN RS
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, b, span, label { color: #00FF00 !important; }
    .stButton>button {
        background-color: #00FF00; color: black; font-weight: bold; width: 100%;
        border-radius: 10px; height: 50px;
    }
    .stSidebar { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.title("🔐 Acceso")
            pin = st.text_input("PIN de acceso", type="password")
            if st.button("Ingresar"):
                if pin == "2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("❌ PIN incorrecto")
        return False
    return True

if verificar_acceso():
    st.sidebar.title("MENU RS")
    menu = st.sidebar.selectbox("Opciones:", ["Panel de Cobranza", "Registrar Nuevo Cliente"])

    # --- MÓDULO 1: COBRANZA (Desde la Nube) ---
    if menu == "Panel de Cobranza":
        st.title("💸 Cobranza en Tiempo Real")
        df = conn.read()
        for idx, row in df.iterrows():
            if str(row.get('nombre')) != "nan":
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"👤 **{row['nombre']}** | 💰 **${row['monto']}**")
                    with c2:
                        tel = str(row.get('teléfono', '')).replace(" ", "")
                        msg = f"Hola {row['nombre']}, recordatorio de pago CrediCheck Pro."
                        link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲 Cobrar</div></a>', unsafe_allow_html=True)
                st.divider()

    # --- MÓDULO 2: REGISTRO (Hacia la Nube) ---
    elif menu == "Registrar Nuevo Cliente":
        st.title("📝 Registro Nuevo")
        with st.form("registro"):
            nombre = st.text_input("Nombre Cliente")
            monto = st.number_input("Monto", min_value=0)
            telefono = st.text_input("Teléfono")
            st.markdown("### 👥 Avales")
            av1 = st.text_input("Aval 1")
            av2 = st.text_input("Aval 2")
            
            if st.form_submit_button("💾 GUARDAR EN GOOGLE SHEETS"):
                # Crear DataFrame con el nuevo dato
                nuevo_dato = pd.DataFrame([{
                    "fecha": datetime.now().strftime("%d/%m/%Y"),
                    "nombre": nombre, "monto": monto, "teléfono": telefono,
                    "aval_1": av1, "aval_2": av2, "estado": "Activo"
                }])
                # Leer datos actuales y concatenar
                df_actual = conn.read()
                df_final = pd.concat([df_actual, nuevo_dato], ignore_index=True)
                conn.update(data=df_final)
                st.success("¡Datos guardados en tu Google Sheet!")
                st.balloons()

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
