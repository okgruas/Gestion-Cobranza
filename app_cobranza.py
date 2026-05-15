import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from streamlit_gsheets import GSheetsConnection  # <--- El nuevo motor

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

# --- FUNCIÓN DE SEGURIDAD (PIN) ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.title("🔐 Acceso")
            pin = st.text_input("Introduce tu PIN de acceso", type="password")
            if st.button("Ingresar"):
                if pin == "2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto")
        return False
    return True

# Solo ejecutamos si el PIN es correcto
if verificar_acceso():
    # 2. CONEXIÓN A GOOGLE SHEETS (El reemplazo del Excel local)
    conn = st.connection("gsheets", type=GSheetsConnection)

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
            # Leemos directamente de la nube
            df = conn.read(ttl=0) # ttl=0 para que siempre traiga datos frescos
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
                                msg = f"Hola *{nombre_cte}*, recordatorio de pago CrediCheck Pro. 📊"
                                link = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{link}" target="_blank"><div style="background-color:#00FF00;color:black;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📲Cobrar</div></a>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("Aún no hay clientes registrados en la nube.")
        except Exception as e:
            st.error(f"Error al conectar con Google Sheets: {e}")

# --- MÓDULO 2: REGISTRO DE NUEVO CLIENTE ---
    if menu == "Registrar Nuevo Cliente":
        st.title("📝 Registro de Nuevo Crédito")
        
        # Obtenemos la fecha actual para el registro
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

            submit = st.form_submit_button("🚀 Guardar en la Nube")

            if submit:
                if nombre and monto > 0 and telefono:
                    try:
                        # 1. Leemos los datos actuales
                        df_actual = conn.read(ttl=0)
                        
                        # 2. Creamos la nueva fila (Asegúrate de que el orden coincida con tus columnas en Excel)
                        nueva_fila = pd.DataFrame([{
                            "fecha": fecha_hoy,
                            "nombre": nombre,
                            "monto": monto,
                            "teléfono": telefono,
                            "aval 1": aval1_nombre,
                            "tel aval 1": aval1_tel,
                            "aval 2": aval2_nombre,
                            "tel aval 2": aval2_tel
                        }])
                        
                        # 3. Concatenamos y subimos
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        conn.update(data=df_final)
                        
                        st.success(f"✅ ¡Registro de {nombre} guardado con éxito!")
                        st.balloons            nuevo_registro = [
                fecha_hoy, nombre, monto, telefono, 
                aval1_nombre, aval1_tel,  # <--- Nuevos campos
                aval2_nombre, aval2_tel   # <--- Nuevos campos
            ]
            # ... resto de tu código para guardar
    # --- PIE DE PÁGINA ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 **Yajaira Leija**\nCapitana Albatros ⚓")
