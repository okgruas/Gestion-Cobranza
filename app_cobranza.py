import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Función para leer los datos publicados (el "túnel" seguro)
def leer_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        return pd.read_csv(csv_url)
    except:
        return None

# 2. SISTEMA DE ACCESO
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN", type="password")
        if st.button("Ingresar"):
            # LINK DE TU HOJA CONTROL (LA QUE TIENE LOS PINs)
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            df_m = leer_datos(url_maestra)
            
            if df_m is not None:
                df_m.columns = df_m.columns.str.strip().lower()
                match = df_m[df_m['pin'].astype(str).str.strip() == pin_usuario.strip()]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                    st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
            else:
                st.error("⚠️ Error de conexión con la base central.")
else:
    # 3. PANTALLA DEL CLIENTE
    st.success(f"Bienvenida: {st.session_state['nombre_cliente']}")
    df_p = leer_datos(st.session_state["url_cliente"])
    if df_p is not None:
        st.write("### Tus Movimientos Actualizados")
        st.dataframe(df_p)
    else:
        st.error("No se pudo cargar tu base personal.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
