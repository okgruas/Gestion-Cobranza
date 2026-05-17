import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN DE LECTURA SIN MEMORIA (CACHE) ---
def cargar_hoja_fresca(url):
    try:
        # Forzamos la descarga directa para que no lea basura de otros correos
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        # Leemos el archivo
        df = pd.read_csv(csv_url)
        # Limpiamos nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# --- LÓGICA DE ACCESO ---
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN", type="password")
        
        if st.button("Entrar"):
            # LINK DE TU GMAIL (LA HOJA VERDE DE CONTROL)
            link_maestro = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            # Limpiamos cualquier rastro de archivos viejos
            st.cache_data.clear()
            base_control = cargar_hoja_fresca(link_maestro)
            
            if base_control is not None:
                # Si detecta las columnas de pagos, avisamos qué está pasando
                if 'pin' not in base_control.columns:
                    st.error(f"⚠️ Error: Sigo leyendo el archivo de pagos. Columnas: {list(base_control.columns)}")
                else:
                    base_control['pin'] = base_control['pin'].astype(str).str.strip()
                    coincidencia = base_control[base_control['pin'] == pin_usuario.strip()]
                    
                    if not coincidencia.empty:
                        st.session_state["logueado"] = True
                        st.session_state["url_especifica"] = coincidencia.iloc[0]['link_excel']
                        st.session_state["nombre_cl"] = coincidencia.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
            else:
                st.error("❌ No hay conexión con la Hoja de Control.")

else:
    # --- VISTA DEL CLIENTE (DESDE EL OTRO CORREO) ---
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    df_cliente = cargar_hoja_fresca(st.session_state["url_especifica"])
    
    if df_cliente is not None:
        st.subheader("Tu Estado de Cuenta")
        st.dataframe(df_cliente, use_container_width=True)
    
    if st.button("Salir"):
        st.session_state["logueado"] = False
        st.rerun()
