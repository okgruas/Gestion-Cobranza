import streamlit as st
import pandas as pd

# 1. ESTILO ALBATROS (Fondo oscuro y cian)
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN DE LECTURA DIRECTA ---
def cargar_excel(url):
    try:
        # Limpiamos el link para que sea descarga directa
        url_limpia = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(url_limpia)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# --- CONTROL DE ACCESO ---
if "entró" not in st.session_state:
    st.session_state["entró"] = False

if not st.session_state["entró"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 Panel Albatros")
        pin = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Despegar"):
            # LINK DE TU HOJA CONTROL (TU GMAIL)
            maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            # Limpiamos memoria antes de buscar
            st.cache_data.clear()
            df_m = cargar_excel(maestra)
            
            if df_m is not None:
                if 'pin' in df_m.columns:
                    df_m['pin'] = df_m['pin'].astype(str).str.strip()
                    usuario = df_m[df_m['pin'] == pin.strip()]
                    
                    if not usuario.empty:
                        st.session_state["entró"] = True
                        st.session_state["url_cl"] = usuario.iloc[0]['link_excel']
                        st.session_state["nombre_cl"] = usuario.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN no registrado.")
                else:
                    st.warning(f"⚠️ Columnas en Control: {list(df_m.columns)}")
            else:
                st.error("❌ No pude conectar con tu Gmail. Revisa el link.")
else:
    # --- PANTALLA DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    # Lee el Excel que está en el correo del cliente
    df_cl = cargar_excel(st.session_state["url_cl"])
    
    if df_cl is not None:
        st.subheader("Estado de Cuenta")
        st.table(df_cl)
    else:
        st.info("Asegúrate de que el Excel del cliente esté 'Publicado en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["entró"] = False
        st.rerun()
