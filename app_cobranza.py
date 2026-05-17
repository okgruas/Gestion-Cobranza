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

# --- FUNCIÓN DE SEGURIDAD (PIN DINÁMICO) ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Acceso")
    pin_ingresado = st.text_input("Introduce tu PIN de acceso", type="password")
        
        if st.button("Ingresar"):
            try:
                # 1. Conectamos a la Hoja Maestra (Control de Renta)
                # El link de la Hoja Maestra debe estar en los Secrets de Streamlit
                conn_maestra = st.connection("gsheets", type=GSheetsConnection, 
                                            spreadsheet=st.secrets["connections"]["gsheets"]["hoja_maestra"])
                df_maestra = conn_maestra.read(ttl=0)
                
                # 2. Buscamos si el PIN que metieron existe
                match = df_maestra[df_maestra['pin'].astype(str) == pin_ingresado]
                
                if not match.empty:
                    st.session_state["autenticado"] = True
                    # Guardamos el link del Excel personal de este cliente
                    st.session_state["url_personal"] = match.iloc[0]['link_excel']
                    st.success(f"✅ Bienvenida, {match.iloc[0]['cliente']}")
                    st.rerun()
                else:
                    st.error("❌ PIN no reconocido o renta vencida")
            except Exception as e:
                st.error("Error de conexión con la central de acceso.")
            # --- CAMBIO AQUÍ: Ahora lee el PIN desde los Secrets ---
            pin_correcto = str(st.secrets["configuracion"]["pin_acceso"])
            
            if st.button("Ingresar"):
                if pin == pin_correcto:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
        return False
    return True

# Solo ejecutamos si el PIN es correcto
if verificar_acceso():
    # --- CAMBIO AQUÍ: Forzamos a que lea el Spreadsheet de los Secrets ---
    pin_correcto = "2026"

    # 3. MENÚ LATERAL
    st.sidebar.title("MENU RS")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    menu = st.sidebar.selectbox("Selecciona una opción:", ["Panel de Cobranza", "Registrar Nuevo Cliente"])

    # --- MÓDULO 1: PANEL DE COBRANZA ---
    if menu == "Panel de Cobranza":
        st.title("💸 CrediCheck - Cobranza")
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
                                msg = f"Hola *{nombre_cte}*, Ya no estamos jugando. Su deuda pasó a cobranza judicial por moroso. Pague ahora o aténgase a las acciones forzosas que estamos por ejecutar contra su patrimonio. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲Cobrar</div></a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("Aún no hay clientes registrados en la nube.")
        except Exception as e:
            st.error(f"Error al conectar con Google Sheets: {e}")

    # --- MÓDULO 2: REGISTRO DE NUEVO CLIENTE ---
    elif menu == "Registrar Nuevo Cliente":
        st.title("📝 Registro de Nuevo Crédito")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        with st.form("registro_cliente"):
            st.markdown("### 👤 Datos del Titular")
            nombre = st.text_input("Nombre Completo del Cliente")
            col_a, col_b = st.columns(2)
            with col_a:
                monto = st.number_input("Monto del Préstamo ($)", min_value=0)
            with col_b:
                telefono = st.text_input("Teléfono (10 dígitos)")
            
            st.markdown("### 🛡️ Información de Avales")
            col1, col2 = st.columns(2)
            with col1:
                aval1_nombre = st.text_input("Nombre Completo - Aval 1")
                aval1_tel = st.text_input("Teléfono - Aval 1")
            with col2:
                aval2_nombre = st.text_input("Nombre Completo - Aval 2")
                aval2_tel = st.text_input("Teléfono - Aval 2")

            st.markdown("### 📊 Estatus del Crédito")
            estado = st.selectbox("Estado Inicial", ["Activo", "Pendiente", "Revisión"])

            submit = st.form_submit_button("🚀 Guardar en la Nube")

            if submit:
                if nombre and monto > 0 and telefono:
                    try:
                        df_actual = conn.read(ttl=0)
                        nueva_fila = pd.DataFrame([{
                            "fecha": fecha_hoy,
                            "nombre": nombre,
                            "monto": monto,
                            "teléfono": telefono,
                            "aval 1": aval1_nombre,
                            "tel aval 1": aval1_tel,
                            "aval 2": aval2_nombre,
                            "tel aval 2": aval2_tel,
                            "estado": estado
                        }])
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        conn.update(data=df_final)
                        st.success(f"✅ ¡Registro de {nombre} guardado con éxito!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.warning("⚠️ Por favor llena los campos obligatorios (Nombre, Monto y Teléfono)")

    # --- PIE DE PÁGINA ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
