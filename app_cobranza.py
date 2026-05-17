import streamlit as st
import pandas as pd

st.set_page_config(page_title="CrediCheck Pro", layout="wide")

# Función especial para leer sin pedir permisos complicados
def leer_excel_publico(url):
    # Convertimos el link de edición en uno de exportación directa
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    csv_url = csv_url.replace('/edit#gid=', '/export?format=csv&gid=')
    if '/edit' in csv_url and '/export' not in csv_url:
        csv_url = csv_url.replace('/edit', '/export?format=csv')
    return pd.read_csv(csv_url)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.title("🔐 Acceso")
        pin_usuario = st.text_input("PIN", type="password")
        if st.button("Ingresar"):
            try:
                # USA TU LINK DE LA HOJA VERDE AQUÍ
                url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
                df_m = leer_excel_publico(url_maestra)
                
                # Limpiar nombres de columnas por si acaso
                df_m.columns = df_m.columns.str.strip().lower()
                
                match = df_m[df_m['pin'].astype(str).str.strip() == pin_usuario.strip()]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                    st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
            except Exception as e:
                st.error("⚠️ Error de conexión. Verifica que el Excel esté en 'Cualquier persona con el enlace'")
else:
    st.success(f"Bienvenido: {st.session_state['nombre_cliente']}")
    try:
        df_p = leer_excel_publico(st.session_state["url_cliente"])
        st.dataframe(df_p)
    except:
        st.error("Error al cargar tu base de datos personal.")
