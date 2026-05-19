import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración visual limpia
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, p, label { color: #E0E0E0 !important; }
    .stButton>button { background-color: #1E1E1E; color: #00FF00; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# Inicializamos la conexión oficial de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        st.write("### Panel de Acceso")
        pin_input = st.text_input("Introduce tu PIN de Seguridad", type="password")
        
        if st.button("Ingresar al Sistema"):
            try:
                # Forzamos la lectura directa de la pestaña 'Control' sin caché (ttl=0)
                df = conn.read(worksheet="Control", ttl=0)
                
                # Estandarizamos las columnas a minúsculas
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                if 'pin' in df.columns:
                    df['pin'] = df['pin'].astype(str).str.strip()
                    usuario = df[df['pin'] == pin_input.strip()]
                    
                    if not usuario.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_user = usuario.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ El PIN ingresado no es correcto.")
                else:
                    st.error("⚠️ Estructura incorrecta: No se detectó la columna 'pin'.")
                    st.info(f"Columnas leídas: {list(df.columns)}")
            except Exception as e:
                st.error(f"Error de conexión con el nuevo origen de datos: {e}")
else:
    # --- PANEL DE CONSULTA DE CLIENTE ---
    user = st.session_state.datos_user
    st.header(f"Bienvenida al Panel, {user['cliente']}")
    
    try:
        # Leemos el archivo individual del cliente configurado en la fila
        df_cliente = conn.read(spreadsheet=user['link_excel'], ttl=0)
        st.subheader("📋 Estado de Cuenta Actualizado")
        st.dataframe(df_cliente, use_container_width=True)
    except Exception as e:
        st.warning("El acceso fue exitoso, pero no se pudo cargar el desglose del cliente.")
        st.caption(f"Detalle técnico: {e}")

    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
