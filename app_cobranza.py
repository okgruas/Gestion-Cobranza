import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. ESTILO NEÓN RS
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, b, span, label { color: #00FF00 !important; }
    .stTextInput>div>div>input { background-color: #111; color: #00FF00; border: 1px solid #00FF00; }
    .stButton>button { background-color: #00FF00; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 50px; }
    .btn-whatsapp { background-color: #00FF00; color: black; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; text-decoration: none; display: block; }
    </style>
    """, unsafe_allow_html=True)

# 2. SEGURIDAD PIN 2026
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 Acceso")
        pin = st.text_input("Introduce PIN", type="password")
        if st.button("Ingresar"):
            if pin == "2026":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ PIN incorrecto")
else:
    # 3. CONEXIÓN REAL A GOOGLE SHEETS
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        st.sidebar.title("MENU COBRANZA")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()

        menu = st.sidebar.selectbox("Opciones:", ["Panel de Cobranza", "Nuevo Registro"])

        if menu == "Panel de Cobranza":
            st.title("💸 Gestión de Cobranza Directa")
            df = conn.read()
            if df is not None and not df.empty:
                df.columns = [str(c).strip().lower() for c in df.columns]
                for idx, row in df.iterrows():
                    nombre = str(row.get('nombre', ''))
                    if nombre and nombre.lower() != "nan":
                        c1, c2 = st.columns([3, 1])
                        with c1: 
                            st.markdown(f"👤 **Cliente:** {nombre}")
                            st.markdown(f"💰 **Monto:** ${row.get('monto', 0)}")
                        with c2:
                            tel = str(row.get('teléfono', '')).replace(" ", "").split('.')[0]
                            msg = f"Hola *{nombre}*, recordatorio de pago pendiente. 📊"
                            link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 Cobrar</a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No hay datos en el Excel.")
        
        elif menu == "Nuevo Registro":
            st.title("📝 Registrar en la Nube")
            with st.form("registro_nube"):
                n = st.text_input("Nombre Completo")
                m = st.number_input("Monto", min_value=0)
                t = st.text_input("Teléfono (10 dígitos)")
                if st.form_submit_button("💾 GUARDAR EN GOOGLE SHEETS"):
                    df_actual = conn.read()
                    nuevo = pd.DataFrame([{"fecha": datetime.now().strftime("%d/%m/%Y"), "nombre": n, "monto": m, "teléfono": t}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(data=df_final)
                    st.success("✅ ¡Guardado con éxito!")
                    st.balloons()

    except Exception as e:
        st.error(f"⚠️ Error de conexión: Revisa tus Secrets en Streamlit.")
        st.info("Asegúrate de que la URL del Excel en Secrets sea la correcta y que el archivo JSON esté bien pegado.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
