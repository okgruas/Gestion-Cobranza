import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Estilo visual
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p, label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN PARA LEER GOOGLE SHEETS ---
def obtener_datos(url):
    try:
        # Convertimos a link de exportación CSV
        enlace_csv = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(enlace_csv)
        # Limpiamos nombres de columnas (quitar espacios y a minúsculas)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

# --- ESTADO DE LA SESIÓN ---
if "conectado" not in st.session_state:
    st.session_state["conectado"] = False

# --- PANTALLA DE ACCESO ---
if not st.session_state["conectado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso de Clientes")
        pin_ingresado = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Ingresar"):
            # LINK FIJO DE TU HOJA DE CONTROL (La que tiene cliente, pin, link_excel)
            # No cambies este link, es el que vi en tus capturas
            url_control = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            base_control = obtener_datos(url_control)
            
            if base_control is not None:
                # Verificamos si existe la columna PIN
                if 'pin' in base_control.columns:
                    # Buscamos el PIN (limpiando espacios)
                    base_control['pin'] = base_control['pin'].astype(str).str.strip()
                    coincidencia = base_control[base_control['pin'] == pin_ingresado.strip()]
                    
                    if not coincidencia.empty:
                        st.session_state["conectado"] = True
                        st.session_state["datos_cliente"] = coincidencia.iloc[0]
                        st.rerun()
                    else:
                        st.error("❌ PIN no encontrado.")
                else:
                    st.warning(f"⚠️ El Excel de Control no tiene columna 'pin'. Columnas reales: {list(base_control.columns)}")
            else:
                st.error("❌ Error de conexión con la Base de Control.")

else:
    # --- PANTALLA DEL CLIENTE (YA LOGUEADO) ---
    cliente = st.session_state["datos_cliente"]
    st.header(f"Bienvenida, {cliente['cliente']}")
    
    # LEER EL EXCEL ESPECÍFICO DEL CLIENTE (el link que está en la columna C)
    df_detalles = obtener_datos(cliente['link_excel'])
    
    if df_detalles is not None:
        st.subheader("Tu Información Detallada")
        st.dataframe(df_detalles, use_container_width=True)
    else:
        st.info("Cargando información adicional...")

    if st.button("Salir"):
        st.session_state["conectado"] = False
        st.rerun()
