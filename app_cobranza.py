import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

def obtener_datos(url):
    try:
        # Convertimos a descarga directa CSV
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

if "sesion" not in st.session_state:
    st.session_state["sesion"] = False

if not st.session_state["sesion"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        pin_ingresado = st.text_input("Introduce tu PIN", type="password")
        
        if st.button("Ingresar"):
            # URL DE TU HOJA DE CONTROL (GMAIL PERSONAL)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            # Limpiamos memoria para forzar lectura de la hoja correcta
            st.cache_data.clear()
            df_control = obtener_datos(url_maestra)
            
            if df_control is not None:
                # Verificamos si leyó la hoja de control o la de pagos
                if 'pin' in df_control.columns:
                    df_control['pin'] = df_control['pin'].astype(str).str.strip()
                    match = df_control[df_control['pin'] == pin_ingresado.strip()]
                    
                    if not match.empty:
                        st.session_state["sesion"] = True
                        st.session_state["link_cliente"] = match.iloc[0]['link_excel']
                        st.session_state["nombre_cl"] = match.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto")
                else:
                    st.error(f"⚠️ Error: La app leyó el archivo de pagos. Columnas: {list(df_control.columns)}")
                    st.info("Asegúrate de que en tu Excel de Control, la pestaña 'Control' sea la primera de la izquierda.")
            else:
                st.error("❌ Error de conexión con Google Sheets")

else:
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    # Lectura del Excel del cliente
    df_pagos = obtener_datos(st.session_state["link_cliente"])
    
    if df_pagos is not None:
        st.subheader("Estado de Cuenta")
        st.dataframe(df_pagos, use_container_width=True)
    else:
        st.warning("No se pudo cargar la información del cliente.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["sesion"] = False
        st.rerun()
