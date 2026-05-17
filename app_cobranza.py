import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Estilo oscuro tipo terminal
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, label { color: #00FFFF !important; }
    .stButton>button { background-color: #00FFFF; color: black; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def leer_datos_limpios(url):
    try:
        # Convertir link de edición a exportación CSV
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        
        # --- LIMPIEZA TOTAL DE COLUMNAS ---
        # Quitamos espacios, pasamos a minúsculas y eliminamos acentos invisibles
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return None

# --- LÓGICA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso de Clientes")
        pin_usuario = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Ingresar"):
            # ESTE ES EL LINK DE TU HOJA "CONTROL"
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            df_control = leer_datos_limpios(url_maestra)
            
            if df_control is not None:
                # Verificamos si existe la columna 'pin' (ya limpia)
                if 'pin' in df_control.columns:
                    # Convertimos todo a texto para comparar sin errores
                    df_control['pin'] = df_control['pin'].astype(str).str.strip()
                    pin_ingresado = str(pin_usuario).strip()
                    
                    usuario = df_control[df_control['pin'] == pin_ingresado]
                    
                    if not usuario.empty:
                        st.session_state["autenticado"] = True
                        st.session_state["url_personal"] = usuario.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = usuario.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto o no registrado.")
                else:
                    # Si falla, te mostrará qué nombres de columna encontró realmente
                    st.warning(f"⚠️ Error de nombres. Columnas encontradas: {list(df_control.columns)}")
            else:
                st.error("❌ Error de conexión. Revisa que el Excel esté en 'Cualquier persona con el enlace'.")

else:
    # --- VISTA CUANDO YA ENTRÓ ---
    st.header(f"Bienvenida, {st.session_state['nombre_cliente']}")
    
    df_cliente = leer_datos_limpios(st.session_state["url_personal"])
    
    if df_cliente is not None:
        st.subheader("Estado de Cuenta Actual")
        st.dataframe(df_cliente, use_container_width=True)
    else:
        st.error("No se pudo cargar la información de tu cuenta.")

    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
