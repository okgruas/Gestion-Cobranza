import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN PARA LEER GOOGLE SHEETS SIN ERRORES ---
def leer_google_sheet(url_directa):
    # Esta línea convierte el link normal en uno de descarga automática
    csv_url = url_directa.replace('/edit#gid=', '/export?format=csv&gid=')
    if '/edit' in csv_url and '/export' not in csv_url:
        csv_url = csv_url.replace('/edit', '/export?format=csv')
    return pd.read_csv(csv_url)

# --- SISTEMA DE ACCESO ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.title("🔐 Acceso")
            pin_usuario = st.text_input("PIN", type="password")
            if st.button("Ingresar"):
                try:
                    # !!! PEGA AQUÍ EL LINK DE TU HOJA VERDE (MAESTRA) !!!
                    url_maestra = "TU_LINK_DE_LA_HOJA_VERDE_AQUI"
                    df_m = leer_google_sheet(url_maestra)
                    
                    # Buscamos el PIN
                    match = df_m[df_m['pin'].astype(str) == pin_usuario]
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto")
                except Exception as e:
                    st.error("⚠️ Error de permisos: Pon el Excel en 'Cualquier persona con el enlace'")
        return False
    return True

# 2. CUERPO DE LA APP
if verificar_acceso():
    st.success(f"Bienvenido: {st.session_state['nombre_cliente']}")
    try:
        # Cargamos los datos del cliente específico
        df_cliente = leer_google_sheet(st.session_state["url_cliente"])
        st.write("### Tus Datos de Cobranza")
        st.dataframe(df_cliente)
    except:
        st.error("No se pudo cargar tu base de datos personal.")
