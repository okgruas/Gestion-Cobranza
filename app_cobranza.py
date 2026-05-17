import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Estilo visual (Fondo negro y letras cyan)
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p, label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN PARA LEER GOOGLE SHEETS ---
def leer_hoja(url):
    try:
        # Forzamos la exportación a CSV para evitar errores de formato
        enlace_csv = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(enlace_csv)
        # Limpieza profunda de nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception:
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
            # LINK FIJO DE TU HOJA DE CONTROL (Donde está Laura Leija)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            base_control = leer_hoja(url_maestra)
            
            if base_control is not None:
                # Verificamos si realmente leyó la hoja de Control
                if 'pin' in base_control.columns:
                    # Convertimos PIN a texto para comparar sin errores
                    base_control['pin'] = base_control['pin'].astype(str).str.strip()
                    usuario = base_control[base_control['pin'] == pin_ingresado.strip()]
                    
                    if not usuario.empty:
                        st.session_state["conectado"] = True
                        st.session_state["datos"] = usuario.iloc[0]
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
                else:
                    st.warning(f"⚠️ Error: La app leyó el archivo equivocado. Columnas detectadas: {list(base_control.columns)}")
            else:
                st.error("❌ No se pudo conectar con la base de datos principal.")

else:
    # --- PANTALLA DEL CLIENTE ---
    datos = st.session_state["datos"]
    st.header(f"Bienvenida, {datos['cliente']}")
    
    # Aquí es donde lee el link específico de ese cliente (Columna C)
    df_cliente = leer_hoja(datos['link_excel'])
    
    if df_cliente is not None:
        st.subheader("Estado de Cuenta")
        st.dataframe(df_cliente, use_container_width=True)
    else:
        st.info("Cargando detalles...")

    if st.button("Cerrar Sesión"):
        st.session_state["conectado"] = False
        st.rerun()
