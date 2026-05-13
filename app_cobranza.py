import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. CONFIGURACIÓN VISUAL NEÓN RS
st.set_page_config(page_title="Cobranza App", layout="wide")
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

# 2. CONEXIÓN A GOOGLE SHEETS
# Asegúrate de configurar los 'Secrets' en Streamlit Cloud con tu JSON de Google
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FUNCIÓN DE SEGURIDAD (PIN)
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
                if pin == "2026": # Tu PIN personalizado
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
        return False
    return True

# 4. CUERPO PRINCIPAL DE LA APP
if verificar_acceso():
    st.sidebar.title("MENU COBRANZA")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    menu = st.sidebar.selectbox("Selecciona una opción:", ["Panel de Cobranza", "Nuevo Registro"])

    # --- MÓDULO: PANEL DE COBRANZA ---
    if menu == "Panel de Cobranza":
        st.title("💸 Cobranza App - Gestión Directa")
        try:
            # Lee los datos directamente de la nube
            df = conn.read()
            
            if not df.empty:
                # Normalizar nombres de columnas
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                for idx, row in df.iterrows():
                    nombre_cte = str(row.get('nombre', 'Sin nombre'))
                    if nombre_cte.lower() != "nan":
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"👤 **Cliente:** {nombre_cte}")
                                st.markdown(f"💰 **Monto Pendiente:** ${row.get('monto', 0)}")
                            with c2:
                                # Limpiar teléfono y crear link de WhatsApp
                                tel = str(row.get('teléfono', '')).replace(" ", "").split('.')[0]
                                msg = f"Hola *{nombre_cte}*, te saludamos de Cobranza App. Recordatorio de pago pendiente. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲 Cobrar</div></a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No hay registros en tu Google Sheet.")
        except Exception as e:
            st.error(f"Error de conexión: Verifica tus Secrets y que el Sheet esté compartido con el correo del JSON.")

    # --- MÓDULO: REGISTRO ---
    elif menu == "Nuevo Registro":
        st.title("📝 Registrar en la Nube")
        with st.form("form_nube"):
            nombre = st.text_input("Nombre Completo")
            monto = st.number_input("Monto", min_value=0)
            telefono = st.text_input("Teléfono (10 dígitos)")
            
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                if nombre and telefono:
                    try:
                        # Leer datos actuales
                        df_actual = conn.read()
                        # Crear nuevo registro
                        nuevo = pd.DataFrame([{
                            "fecha": datetime.now().strftime("%d/%m/%Y"),
                            "nombre": nombre,
                            "monto": monto,
                            "teléfono": telefono,
                            "estado": "Activo"
                        }])
                        # Concatenar y subir a Google Sheets
                        df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                        conn.update(data=df_final)
                        
                        st.success(f"✅ ¡{nombre} guardado correctamente en la nube!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.warning("Por favor rellena el nombre y teléfono.")

    # PIE DE PÁGINA PERSONALIZADO
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
