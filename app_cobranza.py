import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF !important; }</style>", unsafe_allow_html=True)

def leer_datos_ultra_seguro(url):
    try:
        # Forzamos la descarga del CSV
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # LIMPIEZA EXTREMA: Quitamos espacios, pasamos a minúsculas y eliminamos caracteres raros
        df.columns = [str(c).strip().lower().replace(' ', '') for c in df.columns]
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
        pin_usuario = st.text_input("Ingresa tu PIN", type="password")
        if st.button("Ingresar"):
            # TU LINK DE CONTROL
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            df_m = leer_datos_ultra_seguro(url_maestra)
            
            if df_m is not None:
                # BUSCAMOS LA COLUMNA QUE SE PAREZCA A 'PIN'
                col_pin = [c for c in df_m.columns if 'pin' in c]
                
                if col_pin:
                    # Limpiamos los datos de esa columna por si tienen espacios
                    df_m[col_pin[0]] = df_m[col_pin[0]].astype(str).str.strip()
                    match = df_m[df_m[col_pin[0]] == pin_usuario.strip()]
                    
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        # Buscamos columnas de link y nombre de forma flexible
                        c_link = [c for c in df_m.columns if 'link' in c][0]
                        c_nom = [c for c in df_m.columns if 'cliente' in c or 'nombre' in c][0]
                        
                        st.session_state["url_cliente"] = match.iloc[0][c_link]
                        st.session_state["nombre_cliente"] = match.iloc[0][c_nom]
                        st.rerun()
                    else:
                        st.error("❌ PIN no encontrado en la lista.")
                else:
                    # Si falla, te mostramos qué columnas está leyendo la app para corregirlo rápido
                    st.warning(f"⚠️ Columnas detectadas: {list(df_m.columns)}")
                    st.error("No se detectó la columna 'pin'. Asegúrate de que la celda B1 de tu Excel diga 'pin'.")
            else:
                st.error("⚠️ Error de conexión. El Excel no está respondiendo.")
else:
    # --- PANTALLA DEL CLIENTE ---
    st.success(f"Bienvenida: {st.session_state['nombre_cliente']}")
    df_p = leer_datos_ultra_seguro(st.session_state["url_cliente"])
    if df_p is not None:
        st.write("### Estado de Cuenta")
        st.dataframe(df_p)
    else:
        st.error("No se pudo cargar la base personal. Verifica que esté 'Publicada en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
