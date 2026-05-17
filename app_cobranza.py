import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF !important; }</style>", unsafe_allow_html=True)

# Función para leer el Excel que ya publicaste en la web
def leer_datos_seguro(url):
    try:
        # Convierte el link normal en link de descarga directa
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # Solo limpia columnas si el archivo no está vacío
        if not df.empty:
            df.columns = df.columns.str.strip().lower()
        return df
    except:
        return None

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN", type="password")
        if st.button("Ingresar"):
            # LINK DE TU HOJA CONTROL (LA VERDE)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            df_m = leer_datos_seguro(url_maestra)
            
            if df_m is not None and 'pin' in df_m.columns:
                match = df_m[df_m['pin'].astype(str).str.strip() == pin_usuario.strip()]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                    st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
            else:
                st.error("⚠️ Error técnico: Revisa que la pestaña se llame 'Control' y tenga la columna 'pin'.")
else:
    # --- PANTALLA DEL CLIENTE ---
    st.success(f"Bienvenida: {st.session_state['nombre_cliente']}")
    df_p = leer_datos_seguro(st.session_state["url_cliente"])
    if df_p is not None:
        st.write("### Datos de Cobranza")
        st.dataframe(df_p)
    else:
        st.error("No se pudo cargar tu base personal. Verifica que esté 'Publicada en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
