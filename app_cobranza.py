import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- EL LINK DE TU HOJA DE CONTROL (TU GMAIL) ---
# Asegúrate de que este link sea el de la hoja que tiene las columnas: cliente, pin, link_excel
LINK_CONTROL = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"

def leer_excel_directo(url):
    try:
        # Forzamos la descarga limpia
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # Limpieza extrema de títulos
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# --- LÓGICA DE NAVEGACIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso")
        pin_ingresado = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Entrar"):
            # OBLIGAMOS a leer el LINK_CONTROL que definimos arriba
            df_m = leer_excel_directo(LINK_CONTROL)
            
            if df_m is not None:
                # Si encuentra la columna PIN, validamos
                if 'pin' in df_m.columns:
                    df_m['pin'] = df_m['pin'].astype(str).str.strip()
                    usuario = df_m[df_m['pin'] == pin_ingresado.strip()]
                    
                    if not usuario.empty:
                        st.session_state["autenticado"] = True
                        # Guardamos el link del otro correo (el del cliente)
                        st.session_state["url_cliente"] = usuario.iloc[0]['link_excel']
                        st.session_state["nombre"] = usuario.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN no registrado en la hoja de Control.")
                else:
                    # Este mensaje te dirá qué está leyendo realmente
                    st.warning(f"⚠️ ¡Error! Estoy leyendo otro archivo. Columnas detectadas: {list(df_m.columns)}")
            else:
                st.error("❌ No se pudo conectar con la hoja de Control.")
else:
    # --- VISTA DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre']}")
    
    # Aquí es el ÚNICO lugar donde lee el Excel del cliente (del otro correo)
    df_c = leer_excel_directo(st.session_state["url_cliente"])
    
    if df_c is not None:
        st.subheader("Tu Estado de Cuenta")
        st.dataframe(df_c, use_container_width=True)
    else:
        st.info("Asegúrate de que el Excel del cliente esté 'Publicado en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
