import streamlit as st
import pandas as pd

# 1. ESTILO
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

def cargar_datos_seguros(spreadsheet_id, nombre_hoja="Control"):
    try:
        # Forzamos la lectura del ID específico y la hoja específica
        # Esto evita que la llave JSON abra el archivo de avales por error
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

if "acceso" not in st.session_state:
    st.session_state["acceso"] = False

if not st.session_state["acceso"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        st.subheader("Acceso Administrativo")
        pin_user = st.text_input("PIN de Seguridad", type="password")
        
        if st.button("Ingresar Sistema"):
            # ID EXCLUSIVO DE TU HOJA DE CONTROL
            ID_CONTROL = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            
            st.cache_data.clear()
            # Le pedimos específicamente la hoja "Control"
            df_auth = cargar_datos_seguros(ID_CONTROL, "Control")
            
            if df_auth is not None and 'pin' in df_auth.columns:
                df_auth['pin'] = df_auth['pin'].astype(str).str.strip()
                user_match = df_auth[df_auth['pin'] == pin_user.strip()]
                
                if not user_match.empty:
                    st.session_state["acceso"] = True
                    st.session_state["url_cliente"] = user_match.iloc[0]['link_excel']
                    st.session_state["nombre_cl"] = user_match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN no encontrado en la base de datos.")
            else:
                st.warning("⚠️ Error Crítico: La llave JSON sigue abriendo el archivo de Avales.")
                if df_auth is not None:
                    st.info(f"Columnas detectadas: {list(df_auth.columns)}")
                    st.info("Acción: Asegúrate de que la pestaña en tu Excel se llame exactamente 'Control'.")

else:
    # --- VISTA DE DATOS DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    # Extraemos el ID del link del cliente guardado en la hoja de control
    try:
        id_cliente = st.session_state["url_cliente"].split('/d/')[1].split('/')[0]
        df_final = cargar_datos_seguros(id_cliente) # Aquí lee la primera hoja por defecto
        
        if df_final is not None:
            st.write("### Historial y Avales")
            st.dataframe(df_final, use_container_width=True)
    except:
        st.error("No se pudo obtener el ID del archivo del cliente.")

    if st.button("Salir"):
        st.session_state["acceso"] = False
        st.rerun()
