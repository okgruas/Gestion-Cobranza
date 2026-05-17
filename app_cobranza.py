import streamlit as st
import pandas as pd

# 1. ESTILO RELAJANTE PARA LA VISTA
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; } 
    h1, h2, h3, p, label { color: #B0B0B0 !important; }
    .stButton>button { background-color: #1E1E1E; color: #0FF; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

def conectar_directo_gid(spreadsheet_id, gid_number):
    try:
        # Forzamos la descarga del CSV usando el GID numérico exacto
        # El GID 0 suele ser siempre la primera pestaña de la izquierda
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid_number}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        pin_in = st.text_input("Introduce tu PIN", type="password")
        
        if st.button("Acceder al Sistema"):
            # TU ID DE CONTROL
            ID_FILE = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            
            st.cache_data.clear()
            # PROBAMOS CON GID=0 (La primera hoja de tu Excel)
            df_control = conectar_directo_gid(ID_FILE, "0")
            
            if df_control is not None:
                if 'pin' in df_control.columns:
                    df_control['pin'] = df_control['pin'].astype(str).str.strip()
                    user = df_control[df_control['pin'] == pin_in.strip()]
                    
                    if not user.empty:
                        st.session_state["auth"] = True
                        st.session_state["link_cliente"] = user.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = user.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
                else:
                    # Si esto falla, te mostramos qué está leyendo realmente
                    st.error(f"⚠️ Error: Sigo leyendo la hoja de avales.")
                    st.info(f"Columnas detectadas: {list(df_control.columns)}")
                    st.warning("Acción: En tu Excel, arrastra la pestaña 'Control' para que sea la primera a la izquierda.")
            else:
                st.error("❌ No hay conexión con Google Sheets.")

else:
    # --- VISTA DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cliente']}")
    
    # Leemos el archivo del cliente (aquí usamos GID 0 por defecto)
    try:
        id_cl = st.session_state["link_cliente"].split('/d/')[1].split('/')[0]
        df_cl = conectar_directo_gid(id_cl, "0")
        if df_cl is not None:
            st.write("### Estado de Cuenta y Avales")
            st.dataframe(df_cl, use_container_width=True)
    except:
        st.error("Error al procesar el Excel del cliente.")

    if st.button("Cerrar Sesión"):
        st.session_state["auth"] = False
        st.rerun()
