import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF !important; }</style>", unsafe_allow_html=True)

def leer_datos_seguro(url):
    try:
        # Forzamos la descarga del CSV desde el link publicado
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # Limpiamos nombres de columnas: quitamos espacios y pasamos a minúsculas
        df.columns = df.columns.astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        return None

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("Ingresa tu PIN", type="password")
        if st.button("Ingresar"):
            # LINK DE TU HOJA MAESTRA
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            df_m = leer_datos_seguro(url_maestra)
            
            if df_m is not None:
                # Buscamos la columna que contenga la palabra 'pin'
                col_pin = [c for c in df_m.columns if 'pin' in c]
                
                if col_pin:
                    # Limpiamos los datos de la columna PIN para comparar bien
                    df_m[col_pin[0]] = df_m[col_pin[0]].astype(str).str.strip()
                    match = df_m[df_m[col_pin[0]] == pin_usuario.strip()]
                    
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        # Buscamos la columna del link y del cliente
                        col_link = [c for c in df_m.columns if 'link' in c][0]
                        col_nom = [c for c in df_m.columns if 'cliente' in c][0]
                        
                        st.session_state["url_cliente"] = match.iloc[0][col_link]
                        st.session_state["nombre_cliente"] = match.iloc[0][col_nom]
                        st.rerun()
                    else:
                        st.error("❌ PIN no encontrado en la lista.")
                else:
                    st.error("⚠️ No encontré la columna 'pin' en tu Excel. Revisa los títulos.")
            else:
                st.error("⚠️ Error de conexión. Revisa que el Excel esté 'Publicado en la Web'.")
else:
    # --- PANTALLA DEL CLIENTE ---
    st.success(f"Bienvenida: {st.session_state['nombre_cliente']}")
    df_p = leer_datos_seguro(st.session_state["url_cliente"])
    if df_p is not None:
        st.write("### Estado de Cuenta")
        st.table(df_p) # 'table' se ve mejor en celulares
    else:
        st.error("No se pudo cargar tu información personal.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
