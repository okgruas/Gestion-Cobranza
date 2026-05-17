import streamlit as st
import pandas as pd
import time
import random

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN MAESTRA DE LECTURA ---
def leer_archivo_limpio(url):
    try:
        # TRUCO FINAL: Añadimos un número aleatorio al final del link para que sea "único" cada vez
        # Esto obliga a la app a ignorar cualquier memoria guardada.
        separador = "&" if "?" in url else "?"
        url_unica = f"{url.split('/edit')[0]}/export?format=csv{separador}v={random.randint(1, 99999)}"
        
        df = pd.read_csv(url_unica)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

# --- NAVEGACIÓN ---
if "sesion_activa" not in st.session_state:
    st.session_state["sesion_activa"] = False

if not st.session_state["sesion_activa"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso")
        pin_input = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Validar Entrada"):
            # LINK DE TU HOJA DE CONTROL (LA VERDE)
            url_control = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            # Limpiamos la memoria interna de Streamlit
            st.cache_data.clear()
            df_m = leer_archivo_limpio(url_control)
            
            if df_m is not None:
                # Si vemos que sigue leyendo el archivo de pagos, lanzamos un aviso claro
                if 'pin' not in df_m.columns:
                    st.error(f"❌ Error Crítico: Sigo leyendo el archivo de PAGOS. Columnas actuales: {list(df_m.columns)}")
                    st.info("💡 Por favor, ve a tu Excel de Control y asegúrate de que la pestaña 'Control' sea la primera a la izquierda.")
                else:
                    df_m['pin'] = df_m['pin'].astype(str).str.strip()
                    usuario = df_m[df_m['pin'] == pin_input.strip()]
                    
                    if not usuario.empty:
                        st.session_state["sesion_activa"] = True
                        st.session_state["url_cl"] = usuario.iloc[0]['link_excel']
                        st.session_state["nombre_cl"] = usuario.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN no reconocido.")
            else:
                st.error("❌ No hay conexión con el servidor de datos.")

else:
    # --- VISTA PARA EL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    # Leemos el archivo del cliente (del otro correo)
    df_c = leer_archivo_limpio(st.session_state["url_cl"])
    
    if df_c is not None:
        st.subheader("Estado de Cuenta")
        st.dataframe(df_c, use_container_width=True)
    else:
        st.warning("Cargando detalles... Verifica que el Excel del cliente esté 'Publicado en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["sesion_activa"] = False
        st.cache_data.clear()
        st.rerun()
