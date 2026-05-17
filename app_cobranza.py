import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #000; } h1, h2, h3, p { color: #0FF !important; }</style>", unsafe_allow_html=True)

def leer_datos(url):
    try:
        # Convertimos link de edición a link de exportación directa
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        # Limpieza de encabezados
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al leer: {e}")
        return None

# --- ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso de Clientes")
        pin_usuario = st.text_input("Ingresa tu PIN", type="password")
        
        if st.button("Ingresar"):
            # LINK DE TU HOJA "CONTROL" (LA QUE TIENE LOS PINS)
            # Asegúrate de que este link sea el de la hoja con columnas: cliente, pin, link_excel
            url_maestra = "https://docs.google.com/spreadsheets/d/11i_HpvG4p7ftHvX9pSrR52NglxTbZkKTD2wOvQPAwG8/edit"
            
            df_control = leer_datos(url_maestra)
            
            if df_control is not None:
                # Debug para ti: muestra qué columnas encontró en la maestra
                # st.write(f"Columnas en Control: {list(df_control.columns)}") 
                
                if 'pin' in df_control.columns:
                    # Buscamos el PIN
                    df_control['pin'] = df_control['pin'].astype(str).str.strip()
                    usuario = df_control[df_control['pin'] == pin_usuario.strip()]
                    
                    if not usuario.empty:
                        st.session_state["autenticado"] = True
                        # Guardamos los datos del cliente que entró
                        st.session_state["url_personal"] = usuario.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = usuario.iloc[0]['cliente']
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
                else:
                    st.error("⚠️ La hoja de control no tiene una columna llamada 'pin'.")
            else:
                st.error("❌ No pude conectar con la base de datos de control.")

else:
    # --- VISTA DEL CLIENTE ---
    st.header(f"Bienvenida, {st.session_state['nombre_cliente']}")
    
    # Aquí es donde RECIÉN lee el Excel del cliente
    df_cliente = leer_datos(st.session_state["url_personal"])
    
    if df_cliente is not None:
        st.subheader("Tu Estado de Cuenta")
        st.dataframe(df_cliente, use_container_width=True)
    else:
        st.warning("No se pudo cargar tu información detallada.")

    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
