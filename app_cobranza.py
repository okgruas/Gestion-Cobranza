import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y ESTILO NEÓN RS
st.set_page_config(page_title="CrediCheck Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, b, span, label { color: #00FF00 !important; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111; color: #00FF00; border: 1px solid #00FF00;
    }
    .stButton>button {
        background-color: #00FF00; color: black; font-weight: bold; width: 100%;
        border-radius: 10px; height: 50px;
    }
    .stSidebar { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE SEGURIDAD (SISTEMA DE RENTA MULTI-CLIENTE) ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Acceso Clientes")
            pin_usuario = st.text_input("Introduce tu PIN de acceso", type="password")
            
            if st.button("Ingresar"):
                try:
                    # Conecta a la HOJA MAESTRA (La que tiene los PINS y Links)
                    # El link de esta hoja maestra va en los Secrets
                    conn_maestra = st.connection("gsheets", type=GSheetsConnection, 
                                                spreadsheet=st.secrets["connections"]["gsheets"]["hoja_maestra"])
                    df_control = conn_maestra.read(ttl=0)
                    
                    # Buscamos si el PIN existe en tu lista
                    match = df_control[df_control['pin'].astype(str) == pin_usuario]
                    
                    if not match.empty:
                        st.session_state["autenticado"] = True
                        # GUARDAMOS el nombre y el link del excel de ESTE cliente
                        st.session_state["url_cliente"] = match.iloc[0]['link_excel']
                        st.session_state["nombre_cliente"] = match.iloc[0]['cliente']
                        st.success(f"✅ Bienvenida, {st.session_state['nombre_cliente']}")
                        st.rerun()
                    else:
                        st.error("❌ PIN no registrado o renta vencida.")
                except Exception as e:
                    st.error("⚠️ Error de conexión con la base central.")
        return False
    return True

# Ejecución principal
if verificar_acceso():
    # CONEXIÓN AL EXCEL PERSONALIZADO DEL CLIENTE
    conn = st.connection("gsheets", type=GSheetsConnection, spreadsheet="https://docs.google.com/spreadsheets/d/TU_ID_AQUI/edit"

    st.sidebar.title(f"MENU: {st.session_state['nombre_cliente']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    menu = st.sidebar.selectbox("Selecciona una opción:", ["Panel de Cobranza", "Registrar Nuevo Cliente"])

    # --- MÓDULO 1: PANEL DE COBRANZA ---
    if menu == "Panel de Cobranza":
        st.title(f"💸 Cobranza - {st.session_state['nombre_cliente']}")
        try:
            df = conn.read(ttl=0) 
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            if not df.empty:
                for index, row in df.iterrows():
                    nombre_cte = str(row.get('nombre', 'Sin nombre'))
                    if nombre_cte.lower() != "nan" and nombre_cte != "None":
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"👤 **{nombre_cte}**")
                                st.markdown(f"💰 Monto: **${row.get('monto', 0)}**")
                            with c2:
                                tel = str(row.get('teléfono', '')).split('.')[0].replace(" ", "")
                                msg = f"Hola *{nombre_cte}*, le informamos que su saldo de ${row.get('monto', 0)} está pendiente. Por favor regularice su situación. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲Cobrar</div></a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No hay clientes en tu base de datos.")
        except Exception as e:
            st.error(f"Error al leer tus datos: {e}")

    # --- MÓDULO 2: REGISTRO DE NUEVO CLIENTE ---
    elif menu == "Registrar Nuevo Cliente":
        st.title("📝 Registro de Nuevo Crédito")
        with st.form("registro_cliente"):
            nombre = st.text_input("Nombre Completo del Cliente")
            col_a, col_b = st.columns(2)
            with col_a:
                monto = st.number_input("Monto ($)", min_value=0)
            with col_b:
                telefono = st.text_input("Teléfono")
            
            submit = st.form_submit_button("🚀 Guardar en la Nube")

            if submit:
                if nombre and monto > 0:
                    try:
                        df_actual = conn.read(ttl=0)
                        nueva_fila = pd.DataFrame([{"fecha": datetime.now().strftime("%Y-%m-%d"), "nombre": nombre, "monto": monto, "teléfono": telefono}])
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        conn.update(data=df_final)
                        st.success("✅ ¡Guardado!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
