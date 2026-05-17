import streamlit as st
import pandas as pd
from gspread_pandas import Spread

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Gestión Cobranza", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1,h2,h3,p,label { color: #0FF !important; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN PARA LEER USANDO TU LLAVE JSON ---
def leer_con_llave(url_o_id):
    try:
        # Esto usa las credenciales que configuraste en Streamlit Secrets
        # Forzamos a que lea la URL específica y no "lo que encuentre"
        csv_url = url_o_id.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Gestión Cobranza")
        st.subheader("Acceso Administrativo")
        pin_ingresado = st.text_input("PIN de Seguridad", type="password")
        
        if st.button("Ingresar Sistema"):
            # AQUÍ ESTÁ EL TRUCO: Forzamos el ID de tu hoja de CONTROL
            # Para que no se confunda con la de avales/clientes
            ID_CONTROL = "11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8"
            url_maestra = f"https://docs.google.com/spreadsheets/d/{ID_CONTROL}/edit"
            
            st.cache_data.clear()
            df_control = leer_con_llave(url_maestra)
            
            if df_control is not None and 'pin' in df_control.columns:
                df_control['pin'] = df_control['pin'].astype(str).str.strip()
                match = df_control[df_control['pin'] == pin_ingresado.strip()]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                    st.session_state["nombre_cl"] = match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN no válido en la base de Control.")
            else:
                # Si entra aquí, es que sigue leyendo el de avales
                st.warning("⚠️ La llave JSON está abriendo el archivo de Avales/Clientes por error.")
                st.info(f"Columnas detectadas: {list(df_control.columns) if df_control is not None else 'Ninguna'}")

else:
    # --- PANEL DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cl']}")
    
    # Ahora sí, leemos el archivo de datos del cliente
    df_datos = leer_con_llave(st.session_state["url_cliente"])
    
    if df_datos is not None:
        st.write("### Información de Avales y Pagos")
        st.dataframe(df_datos, use_container_width=True)
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
