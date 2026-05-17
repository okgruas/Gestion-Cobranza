import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Estilo para que se vea profesional en el cel
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

def descargar_excel(url):
    try:
        # Forzamos la descarga como CSV para ignorar temas de cuentas/correos
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # Limpiamos nombres de columnas (minúsculas y sin espacios)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

if "acceso" not in st.session_state:
    st.session_state["acceso"] = False

if not st.session_state["acceso"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Panel de Control")
        pin_ingresado = st.text_input("PIN de Acceso", type="password")
        
        if st.button("Entrar"):
            # LINK DE TU HOJA DE CONTROL (TU GMAIL)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            df_m = descargar_excel(url_maestra)
            
            if df_m is not None:
                # Buscamos la columna PIN
                col_pin = [c for c in df_m.columns if 'pin' in c]
                if col_pin:
                    df_m[col_pin[0]] = df_m[col_pin[0]].astype(str).str.strip()
                    match = df_m[df_m[col_pin[0]] == pin_ingresado.strip()]
                    
                    if not match.empty:
                        st.session_state["acceso"] = True
                        # Buscamos el link del otro correo y el nombre
                        c_link = [c for c in df_m.columns if 'link' in c][0]
                        c_nom = [c for c in df_m.columns if 'cliente' in c or 'nombre' in c][0]
                        
                        st.session_state["url_cliente"] = match.iloc[0][c_link]
                        st.session_state["nombre"] = match.iloc[0][c_nom]
                        st.rerun()
                    else:
                        st.error("❌ PIN no registrado")
                else:
                    st.error("⚠️ No encontré la columna 'pin' en tu hoja de control.")
            else:
                st.error("❌ No pude leer tu Excel. ¿Ya lo pusiste en 'Publicar en la web'?")

else:
    # --- PANTALLA DEL CLIENTE (DESDE SU PROPIO CORREO) ---
    st.header(f"Bienvenida, {st.session_state['nombre']}")
    
    # Aquí el código va y busca el Excel que está en el otro correo
    df_c = descargar_excel(st.session_state["url_personal"])
    
    if df_c is not None:
        st.subheader("Estado de Cuenta Actualizado")
        st.dataframe(df_c, use_container_width=True)
    else:
        st.warning("Cargando datos... Asegúrate de que el Excel del cliente también esté 'Publicado en la web'.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["acceso"] = False
        st.rerun()
