import streamlit as st
import base64
import json
import asyncio # Para manejar operaciones asíncronas
import requests # Necesario para hacer llamadas HTTP a la API de Gemini

# Variables globales para Firebase (obligatorias, aunque no se usen para persistencia en este ejemplo de Streamlit)
# Estas variables son proporcionadas por el entorno de Canvas.
# Se usa globals().get() para verificar si la variable existe en el ámbito global de Python.
app_id = globals().get('__app_id', 'default-app-id')
firebase_config_str = globals().get('__firebase_config', '{}')
firebase_config = json.loads(firebase_config_str)
initial_auth_token = globals().get('__initial_auth_token', None)

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Recepcionista IA para Taller de Desabolladura y Pintura",
    page_icon="🚗",
    layout="centered"
)

# Estilos CSS personalizados para una mejor apariencia
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2em;
        color: #333;
        text-align: center;
        margin-bottom: 30px;
    }
    .stFileUploader > div > div > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1em;
        border: none;
        cursor: pointer;
    }
    .stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 8px;
        padding: 12px 25px;
        font-size: 1.1em;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%;
        margin-top: 20px;
    }
    .stButton > button:hover {
        background-color: #007B9E;
    }
    .chat-message {
        background-color: #f0f2f6;
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #e6f7ff;
        align-self: flex-end;
        text-align: right;
    }
    .ai-message {
        background-color: #f0f0f0;
        align-self: flex-start;
        text-align: left;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .stTextArea > label {
        font-weight: bold;
        color: #1E90FF;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicializar el historial de chat si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Función para llamar a la API de Gemini
async def call_gemini_api(prompt_text, image_data=None, chat_history_context=None):
    """
    Llama a la API de Gemini para generar contenido.
    Args:
        prompt_text (str): El mensaje del usuario o la instrucción para la IA.
        image_data (str, optional): Datos de la imagen en base64. Defaults to None.
        chat_history_context (list, optional): Historial de chat para contexto conversacional. Defaults to None.
    Returns:
        str: La respuesta de la IA.
    """
    # Construir el payload para la API
    payload_contents = []

    # Añadir el historial de chat para contexto conversacional
    if chat_history_context:
        for msg in chat_history_context:
            if msg["role"] in ["user", "model"]:
                payload_contents.append(msg)

    # Añadir el mensaje actual del usuario al payload
    user_parts = [{"text": prompt_text}]
    if image_data:
        user_parts.append({
            "inlineData": {
                "mimeType": "image/jpeg", # Asumimos JPEG, puedes ajustar si es necesario
                "data": image_data
            }
        })
    payload_contents.append({"role": "user", "parts": user_parts})

    payload = {"contents": payload_contents}

    # Leer la API Key de Streamlit Secrets o dejarla vacía para el entorno de Canvas
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        api_key = "" # Deja esto vacío si dependes de la inyección de Canvas o si no tienes una clave local.
        # st.warning("No se encontró 'GEMINI_API_KEY' en `secrets.toml`. La aplicación podría no funcionar correctamente sin una clave de API.")


    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        # st.write("Analizando con IA... por favor espera.") # Esto ya se maneja con st.spinner
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, json=payload)
        result = response.json()

        ai_text = "No pude obtener una respuesta de la IA. Inténtalo de nuevo."
        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Para el propósito de este demo, aún mantendremos la simulación para la valoración detallada
        # ya que Gemini-2.0-flash no está entrenado específicamente para cuantificar daños vehiculares.
        if image_data:
            simulated_ai_response = f"""
            ¡Hola! Soy tu recepcionista IA. He analizado la imagen que me has enviado.
            **Marca:** Posiblemente [Marca detectada, ej. Ford]
            **Modelo:** Posiblemente [Modelo detectado, ej. Ranger]
            **Año:** Estimado [Año, ej. 2020]
            **Lugar del siniestro:** [Parte del vehículo, ej. Parachoques trasero y portalón]
            **Tipo de siniestro:** [Tipo de daño, ej. Abolladura en parachoques cromado y rayones en portalón]
            **Estimación de costo desde:** $ [Cantidad, ej. 250.000 CLP]

            Esta es una **estimación inicial basada en la imagen simulada**. Para un presupuesto exacto y definitivo, te recomendamos encarecidamente agendar una visita a nuestro taller para una inspección física detallada.
            """
            # Combinamos la respuesta real de Gemini (si la hay) con la simulación
            # Solo si Gemini dio una respuesta diferente a la predeterminada, la agregamos.
            if ai_text != "No pude obtener una respuesta de la IA. Inténtalo de nuevo.":
                 ai_text = simulated_ai_response + "\n\n**Análisis general de Gemini:** " + ai_text
            else:
                 ai_text = simulated_ai_response # Si Gemini no dio una respuesta útil, solo usamos la simulación
        else:
            # Si no hay imagen, la IA responderá de forma conversacional usando la respuesta real de Gemini
            pass # ai_text ya contiene la respuesta de Gemini o el mensaje de error

        st.session_state.chat_history.append({"role": "model", "parts": [{"text": ai_text}]})
        return ai_text

    except Exception as e:
        error_message = f"Ocurrió un error al comunicarse con la IA: {e}. Por favor, inténtalo de nuevo."
        st.session_state.chat_history.append({"role": "model", "parts": [{"text": error_message}]})
        return error_message

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>🚗 Recepcionista IA para Taller de Desabolladura y Pintura 🎨</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Sube una foto de tu vehículo con un siniestro y obtén una estimación de costo inicial.</p>", unsafe_allow_html=True)

# Sección de carga de imagen
st.subheader("1. Sube una foto de tu vehículo")
uploaded_file = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"])

image_data_base64 = None
if uploaded_file is not None:
    # Mostrar la imagen subida
    st.image(uploaded_file, caption="Imagen subida.", use_container_width=True)
    # Convertir la imagen a base64
    bytes_data = uploaded_file.getvalue()
    image_data_base64 = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("Analizar Daño con IA"):
        # Añadir un mensaje de usuario al historial indicando que se subió una imagen
        st.session_state.chat_history.append({"role": "user", "parts": [{"text": "He subido una imagen de mi vehículo para análisis."}]})

        with st.spinner("Analizando la imagen..."):
            # Este es el prompt interno para la IA, no se muestra al usuario directamente en el chat
            prompt_for_image_analysis = """
            Actúa como un recepcionista de un taller de desabolladura y pintura.
            Analiza la imagen de este vehículo con un siniestro.
            Describe lo que ves en la imagen en términos de tipo de vehículo, color, y la naturaleza general del daño.
            No intentes identificar marca, modelo, año o dar una estimación de costo aquí, solo una descripción general.
            """
            response = asyncio.run(call_gemini_api(prompt_for_image_analysis, image_data=image_data_base64, chat_history_context=list(st.session_state.chat_history)))
            st.rerun() # Para refrescar la interfaz y mostrar el nuevo mensaje

st.subheader("2. Conversa con el recepcionista IA")

# Mostrar historial de chat
for message in st.session_state.chat_history:
    if message["role"] == "user":
        text_content = ""
        for part in message["parts"]:
            if "text" in part:
                text_content += part["text"]
        st.markdown(f"<div class='chat-message user-message'><b>Tú:</b> {text_content}</div>", unsafe_allow_html=True)
    elif message["role"] == "model":
        st.markdown(f"<div class='chat-message ai-message'><b>Recepcionista IA:</b> {message['parts'][0]['text']}</div>", unsafe_allow_html=True)

# Entrada de texto para el usuario
user_input = st.text_input("Escribe tu mensaje aquí:", key="user_input")

if user_input:
    # Si el usuario ingresa texto, añade el mensaje al historial de chat
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_input}]})
    with st.spinner("Pensando..."):
        # Se envía el historial completo para que la IA tenga contexto
        response = asyncio.run(call_gemini_api(user_input, chat_history_context=list(st.session_state.chat_history)))
    st.rerun() # Para refrescar la interfaz y mostrar el nuevo mensaje
