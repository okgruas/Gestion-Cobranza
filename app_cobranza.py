import streamlit as st
import pandas as pd
import random

# Configuración visual para descansar la vista
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #0E1117; } h1,h2,p,label { color: #E0E0E0 !important; }</style>", unsafe_allow_html=True)

def leer_excel_fresco(url_base):
    try:
        # Generamos un número aleatorio para romper la memoria de Google
        rompe_cache = random.randint(1, 999999)
        # Forzamos la descarga del CSV de la primera pestaña (gid=0)
        url_final = f"{url_base}/export?format=csv&gid=0&cache={rompe_cache}"
        df = pd.read_csv(url_final)
        # Limpieza estándar de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

if "sesion" not in st.session_state:
    st.session_state["sesion"] = False

if not st.session_state["sesion"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        pin_test = st.text_input("PIN de Seguridad", type="password")
        
        if st.button("Validar Entrada"):
            # TU ID DE ARCHIVO DE CONTROL
            ID_FILE = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            URL_BASE = f"https://docs.google.com/spreadsheets/d/{ID_FILE}"
            
            st.cache_data.clear() # Limpieza local de Streamlit
            df_auth = leer_excel_fresco(URL_BASE)
            
            if df_auth is not None:
                if 'pin' in df_auth.columns:
                    df_auth['pin'] = df_auth['pin'].astype(str).str.strip()
                    # Tu PIN guardado es 1990
                    match = df_auth[df_auth['pin'] == pin_test.strip()]
                    
                    if not match.empty:
                        st.session_state["sesion"] = True
                        st.session_state["u_data"] = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ El PIN no coincide con los registros actuales.")
                else:
                    # Si esto sale, te dirá qué está viendo realmente el sistema
                    st.error("⚠️ Sigo leyendo las columnas de avales.")
                    st.info(f"Columnas detectadas: {list(df_auth.columns)}")
            else:
                st.error("❌ Error de conexión. Revisa que el archivo sea compartido.")
else:
    st.header(f"Bienvenida al Panel")
    user = st.session_state["u_data"]
    st.success(f"Conectado como: {user['cliente']}")
    
    if st.button("Cerrar Sesión"):
        st.session_state["sesion"] = False
        st.rerun()
