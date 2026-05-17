import streamlit as st
import pandas as pd

# 1. ESTILO RELAJANTE (Gris oscuro para tus ojitos)
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #121212; } h1,h2,p { color: #BBB !important; }</style>", unsafe_allow_html=True)

def cargar_csv_publico(url_publica):
    try:
        # Forzamos a que no use caché guardada
        df = pd.read_csv(url_publica)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

if "acceso_ok" not in st.session_state:
    st.session_state["acceso_ok"] = False

if not st.session_state["acceso_ok"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        pin_ingresado = st.text_input("PIN de Seguridad", type="password")
        
        if st.button("Ingresar"):
            # PEGA AQUÍ EL LINK DE "PUBLICAR EN LA WEB" (EL QUE TERMINA EN .csv)
            LINK_CONTROL_CSV = "TU_LINK_AQUI" 
            
            st.cache_data.clear()
            df_auth = cargar_csv_publico(LINK_CONTROL_CSV)
            
            if df_auth is not None and 'pin' in df_auth.columns:
                df_auth['pin'] = df_auth['pin'].astype(str).str.strip()
                match = df_auth[df_auth['pin'] == pin_ingresado.strip()]
                
                if not match.empty:
                    st.session_state["acceso_ok"] = True
                    st.session_state["datos_usuario"] = match.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto.")
            else:
                st.error("⚠️ Error: El link de publicación no es válido o no tiene la columna 'pin'.")
else:
    # --- PANEL DEL CLIENTE ---
    u = st.session_state["datos_usuario"]
    st.header(f"Bienvenida, {u['cliente']}")
    
    # Aquí puedes seguir usando tu lógica para el Excel del cliente
    st.info("Ya estás dentro del sistema.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["acceso_ok"] = False
        st.rerun()
