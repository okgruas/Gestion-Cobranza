import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# Función con 'cache_data' desactivado para que no se guarden archivos viejos
def leer_excel_fresco(url):
    try:
        # Forzamos link de descarga directa CSV
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        # Leemos el archivo sin guardar nada en la memoria de la app
        df = pd.read_csv(csv_url)
        # Limpieza radical de nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# --- REINICIO TOTAL ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN de Acceso", type="password")
        
        if st.button("Verificar PIN"):
            # LINK DE TU HOJA DE CONTROL (TU GMAIL PRINCIPAL)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            # Borramos cualquier rastro del archivo anterior antes de leer
            st.cache_data.clear() 
            df_m = leer_excel_fresco(url_maestra)
            
            if df_m is not None:
                # Buscamos la columna PIN
                col_pin = [c for c in df_m.columns if 'pin' in c]
                if col_pin:
                    df_m[col_pin[0]] = df_m[col_pin[0]].astype(str).str.strip()
                    match = df_m[df_m[col_pin[0]] == pin_usuario.strip()]
                    
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        # Buscamos el link del otro Excel y el nombre
                        c_link = [c for c in df_m.columns if 'link' in c][0]
                        c_nom = [c for c in df_m.columns if 'cliente' in c or 'nombre' in c][0]
                        
                        st.session_state["url_cliente"] = match.iloc[0][c_link]
                        st.session_state["nombre"] = match.iloc[0][c_nom]
                        st.rerun()
                    else:
                        st.error("❌ PIN no registrado en Control.")
                else:
                    st.warning(f"⚠️ Leyendo archivo equivocado. Columnas: {list(df_m.columns)}")
            else:
                st.error("❌ No pude conectar con la Hoja de Control.")

else:
    # --- PANTALLA DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre']}")
    
    # Aquí lee el Excel que está en el otro correo/cuenta
    df_c = leer_excel_fresco(st.session_state["url_cliente"])
    
    if df_c is not None:
        st.subheader("Información de Cobranza")
        st.dataframe(df_c, use_container_width=True)
    else:
        st.info("Asegúrate de que el Excel del cliente esté 'Publicado en la web'.")
    
    if st.button("Cerrar Sesión"):
        # Al salir, borramos todo para que el siguiente cliente no vea basura
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
