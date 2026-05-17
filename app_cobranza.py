import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. ESTILO RELAJANTE
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #121212; } h1,h2,p { color: #BBB !important; }</style>", unsafe_allow_html=True)

# Conexión oficial (Usa los secretos que ya configuraste)
conn = st.connection("gsheets", type=GSheetsConnection)

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        pin_in = st.text_input("PIN de Acceso", type="password")
        
        if st.button("Entrar"):
            # ID DE TU COPIA NUEVA O ACTUAL
            URL_CONTROL = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            try:
                # Leemos la pestaña 'Control' de forma oficial
                df = conn.read(spreadsheet=URL_CONTROL, worksheet="Control", ttl=0)
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                if 'pin' in df.columns:
                    df['pin'] = df['pin'].astype(str).str.strip()
                    user = df[df['pin'] == pin_in.strip()]
                    
                    if not user.empty:
                        st.session_state["auth"] = True
                        st.session_state["cliente"] = user.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
                else:
                    st.error("⚠️ No encuentro la columna 'pin'. Revisa el nombre en el Excel.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
else:
    st.header(f"Bienvenida, {st.session_state['cliente']['cliente']}")
    
    # Cargar datos del cliente
    try:
        url_cl = st.session_state["cliente"]["link_excel"]
        df_cl = conn.read(spreadsheet=url_cl, ttl=0)
        st.dataframe(df_cl, use_container_width=True)
    except:
        st.error("No se pudo cargar el archivo del cliente.")

    if st.button("Salir"):
        st.session_state["auth"] = False
        st.rerun()
