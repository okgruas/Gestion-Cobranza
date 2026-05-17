import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL (Colores más suaves para tus ojos)
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; } /* Un gris muy oscuro, menos pesado que el negro puro */
    h1, h2, h3, p, label { color: #E0E0E0 !important; } /* Blanco suave, no brilla tanto */
    .stButton>button { background-color: #262730; color: #0FF; border: 1px solid #0FF; }
    </style>
    """, unsafe_allow_html=True)

def obtener_datos_directos(spreadsheet_id, hoja="Control"):
    try:
        # Este link es "mágico": obliga a Google a darte UNA HOJA específica por su nombre
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={hoja}"
        df = pd.read_csv(url)
        # Limpiamos los nombres de las columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

# --- LÓGICA DE ACCESO ---
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        st.write("### Acceso Administrativo")
        # Tu PIN es 1990 según tu Excel
        pin_ingreso = st.text_input("PIN de Seguridad", type="password", help="Introduce tu código de 4 dígitos")
        
        if st.button("Entrar al Sistema"):
            # ID de tu archivo de CONTROL
            ID_CONTROL = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            
            st.cache_data.clear()
            # Forzamos que lea la pestaña que se llama exactamente 'Control'
            df_control = obtener_datos_directos(ID_CONTROL, "Control")
            
            if df_control is not None and 'pin' in df_control.columns:
                df_control['pin'] = df_control['pin'].astype(str).str.strip()
                busqueda = df_control[df_control['pin'] == pin_ingreso.strip()]
                
                if not busqueda.empty:
                    st.session_state["logueado"] = True
                    st.session_state["datos_cl"] = busqueda.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ El PIN no es correcto.")
            else:
                # Si esto sale, es que Google mandó la hoja de avales otra vez
                st.error("⚠️ Error Crítico de Lectura")
                if df_control is not None:
                    st.info(f"Columnas encontradas: {list(df_control.columns)}")
                    st.warning("Revisa que la pestaña en tu Excel se llame exactamente 'Control' con la 'C' mayúscula.")

else:
    # --- PANEL PRINCIPAL (AQUÍ YA ENTRASTE) ---
    st.header(f"Bienvenida al Sistema")
    cliente = st.session_state["datos_cl"]
    st.success(f"Sesión activa: {cliente['cliente']}")
    
    # Intentamos cargar el archivo específico del cliente que está en la columna C
    try:
        # Extraemos el ID del link largo del cliente
        id_cliente_excel = cliente['link_excel'].split('/d/')[1].split('/')[0]
        df_pagos = obtener_datos_directos(id_cliente_excel) # Aquí lee la primera hoja por defecto
        
        if df_pagos is not None:
            st.subheader("📋 Información de Pagos y Avales")
            st.dataframe(df_pagos, use_container_width=True)
        else:
            st.info("No se encontraron registros en el archivo del cliente.")
    except:
        st.error("El enlace al Excel del cliente no es válido.")

    if st.button("Cerrar Sesión"):
        st.session_state["logueado"] = False
        st.rerun()
