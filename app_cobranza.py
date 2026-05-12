import streamlit as st
import pandas as pd
import urllib.parse
import os
from datetime import datetime
from PIL import Image

# 1. CONFIGURACIÓN Y ESTILO NEÓN RS
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
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE SEGURIDAD (PIN) ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Acceso")
            pin = st.text_input("Introduce tu PIN de acceso", type="password")
            if st.button("Ingresar"):
                if pin == "2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
        return False
    return True

# Solo ejecutamos el resto si el PIN es correcto
if verificar_acceso():
    # Asegurar que existan las carpetas
    for folder in ["documentos", "biometria"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    DB_FILE = "base_datos_prestamos.xlsx"

    # 2. MENÚ LATERAL
    st.sidebar.title("MENU RS")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    menu = st.sidebar.selectbox("Selecciona una opción:", ["Panel de Cobranza", "Registrar Nuevo Cliente"])

    # --- MÓDULO 1: PANEL DE COBRANZA ---
    if menu == "Panel de Cobranza":
        st.title("💸 CrediCheck - Cobranza")
        try:
            if os.path.exists(DB_FILE):
                df = pd.read_excel(DB_FILE)
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                for index, row in df.iterrows():
                    nombre_cte = str(row.get('nombre', 'Sin nombre'))
                    if nombre_cte.lower() != "nan":
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"👤 **{nombre_cte}**")
                                st.markdown(f"💰 Monto: **${row.get('monto', 0)}**")
                            with c2:
                                tel = str(row.get('teléfono', '')).split('.')[0].replace(" ", "")
                                msg = f"Hola *{nombre_cte}*, recordatorio de pago CrediCheck Pro. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲Cobrar</div></a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("Aún no hay clientes registrados.")
        except Exception as e:
            st.error(f"Error al leer la base de datos: {e}")

    # --- MÓDULO 2: REGISTRO ---
    elif menu == "Registrar Nuevo Cliente":
        st.title("📝 Registro de Nuevo Cliente")
        
        with st.form("form_registro"):
            st.markdown("### 👤 Datos del Cliente")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo del Cliente")
                monto = st.number_input("Monto del Préstamo", min_value=0)
            with col2:
                telefono = st.text_input("Teléfono Cliente")
                fecha = st.date_input("Fecha de Préstamo", datetime.now())

            st.markdown("### 👥 Avales")
            col3, col4 = st.columns(2)
            with col3:
                nombre_aval1 = st.text_input("Nombre Aval 1")
                tel_aval1 = st.text_input("Teléfono Aval 1")
            with col4:
                nombre_aval2 = st.text_input("Nombre Aval 2")
                tel_aval2 = st.text_input("Teléfono Aval 2")

            st.markdown("### 🪪 Documentación")
            c_ine1, c_ine2, c_foto = st.columns(3)
            with c_ine1: f_frente = st.file_uploader("INE Frente", type=['jpg', 'png'])
            with c_ine2: f_vuelta = st.file_uploader("INE Vuelta", type=['jpg', 'png'])
            with c_foto: f_perfil = st.file_uploader("Foto Cliente", type=['jpg', 'png'])

            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                if nombre and telefono:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    id_usuario = nombre.replace(" ", "_")
                    
                    if f_perfil:
                        Image.open(f_perfil).save(f"biometria/{id_usuario}_perfil_{timestamp}.png")
                    
                    nuevo_registro = {
                        "fecha": fecha.strftime("%d/%m/%Y"),
                        "nombre": nombre,
                        "monto": monto,
                        "teléfono": telefono,
                        "aval_1": nombre_aval1,
                        "tel_aval_1": tel_aval1,
                        "aval_2": nombre_aval2,
                        "tel_aval_2": tel_aval2,
                        "estado": "Activo"
                    }
                    
                    # Guardar en Excel
                    if os.path.exists(DB_FILE):
                        df_ex = pd.read_excel(DB_FILE)
                        pd.concat([df_ex, pd.DataFrame([nuevo_registro])], ignore_index=True).to_excel(DB_FILE, index=False)
                    else:
                        pd.DataFrame([nuevo_registro]).to_excel(DB_FILE, index=False)
                        
                    st.success(f"✅ ¡{nombre} guardado correctamente!")
                    st.balloons()
                else:
                    st.error("Falta nombre o teléfono.")

    # --- PIE DE PÁGINA ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")