import streamlit as st
from google import genai
from google.genai import types

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==============================================================================
st.set_page_config(
    page_title="Asistente AI - Sistemas Inteligentes",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Asistente Virtual 'Astra'")
st.caption("UAdeO • Materia: Sistemas Inteligentes • Dra. Aiblis Susej Herrera Palafox")

# ==============================================================================
# 2. GESTIÓN SEGURA DE LA API KEY (LOCAL Y STREAMLIT CLOUD)
# ==============================================================================
try:
    # Intenta leer la clave desde los secretos de Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    # ⚠️ REEMPLAZA ESTA CADENA POR TU CLAVE REAL DE GOOGLE AI STUDIO PARA PRUEBAS LOCALES
    api_key = "No se encontró la API Key. Configúrala en los secretos de Streamlit."

# ==============================================================================
# 3. CONFIGURACIÓN DE PERSONALIDAD DEL BOT
# ==============================================================================
CONFIG_INSTRUCCIONES = types.GenerateContentConfig(
    system_instruction=(
        "Eres 'Astra', un asistente académico inteligente, formal y estructurado para la materia "
        "Sistemas Inteligentes de la UAdeO. Tu objetivo es explicar conceptos de Inteligencia Artificial, "
        "Agentes y Redes Neuronales de forma clara y accesible. Si te preguntan por entregas o fechas, "
        "indica amablemente que deben verificar las indicaciones de la Dra. Aiblis Susej Herrera Palafox."
    ),
    temperature=0.7
)

# ==============================================================================
# 4. INICIALIZACIÓN PERSISTENTE EN MEMORIA (PREVIENE ERRORES DE CONEXIÓN)
# ==============================================================================
# Se guarda tanto el cliente como el chat en st.session_state para mantenerlos vivos
if "client" not in st.session_state or st.session_state.get("current_api_key") != api_key:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.current_api_key = api_key
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-3.8-flash",
        config=CONFIG_INSTRUCCIONES
    )

# Historial gráfico de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy Astra. ¿En qué tema de Sistemas Inteligentes te puedo ayudar hoy?"}
    ]

# ==============================================================================
# 5. BARRA LATERAL (OPCIONES DE REINICIO)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Opciones del Agente")
    st.markdown("Modelo backend: **Gemini 3.8 Flash**")
    if st.button("🧹 Limpiar Conversación"):
        st.session_state.chat_session = st.session_state.client.chats.create(
            model="gemini-3.8-flash",
            config=CONFIG_INSTRUCCIONES
        )
        st.session_state.messages = [
            {"role": "assistant", "content": "🧹 La sesión ha sido reiniciada. ¿Qué otra duda tienes?"}
        ]
        st.rerun()

# ==============================================================================
# 6. RENDERIZADO DEL HISTORIAL DE MENSAJES
# ==============================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==============================================================================
# 7. ENTRADA DE TEXTO Y PROCESAMIENTO
# ==============================================================================
if user_input := st.chat_input("Escribe tu pregunta o duda aquí..."):
    # Renderizar el mensaje del usuario de inmediato
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generar la respuesta llamando a la API de Gemini
    with st.chat_message("assistant"):
        with st.spinner("Pensando respuesta..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ Error al consultar la API: {e}")