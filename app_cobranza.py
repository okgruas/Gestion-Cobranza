import streamlit as st
import pandas as pd

# 1. ESTILO RELAJANTE (Gris oscuro y blanco suave para no cansar la vista)
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; } 
    h1, h2, h3, p, label { color: #DCDCDC !important; }
    .stButton>button { background-color: #1E1E1E; color: #0FF; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

def lectura_infalible(spreadsheet_id, gid="0"):
    try:
        # TRUCO MAESTRO: Usamos el GID (ID de la pestaña) en lugar del nombre.
        # Por defecto, la primera pestaña siempre es GID=0.
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        st.write("### Acceso al Sistema")
        pin_ingreso = st.text_input("PIN de Seguridad", type="password")
        
        if st.button("Entrar"):
            # TU ID DE CONTROL
            ID_MAESTRO = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            
            st.cache_data.clear()
            # Forzamos la lectura de la pestaña con GID=0 (La primera a la izquierda)
            df_auth = lectura_infalible(ID_MAESTRO, gid="0")
            
            if df_auth is not None:
                if 'pin' in df_auth.columns:
                    df_auth['pin'] = df_auth['pin'].astype(str).str.strip()
                    match = df_auth[df_auth['pin'] == pin_ingreso.strip()]
                    
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        st.session_state["data"] = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
                else:
                    # Si esto sale, te diré qué GID tiene la hoja que SÍ tiene el PIN
                    st.error("⚠️ Sigo en la hoja equivocada.")
                    st.info(f"Columnas detectadas: {list(df_auth.columns)}")
            else:
                st.error("❌ Error de conexión.")

else:
    # --- PANEL DEL CLIENTE ---
    user = st.session_state["data"]
    st.header(f"Bienvenida, {user['cliente']}")
    
    # Leemos el archivo del cliente
    try:
        id_cl = user['link_excel'].split('/d/')[1].split('/')[0]
        df_cl = lectura_infalible(id_cl)
        if df_cl is not None:
            st.write("### Datos de Cobranza")
            st.dataframe(df_cl, use_container_width=True)
    except:
        st.error("Error al cargar el Excel del cliente.")

    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
