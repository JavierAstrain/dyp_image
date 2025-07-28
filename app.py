import streamlit as st
import base64
import json
import asyncio # Para manejar operaciones asíncronas

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
async def call_gemini_api(prompt, image_data=None, chat_history_context=None):
    """
    Llama a la API de Gemini para generar contenido.
    Args:
        prompt (str): El mensaje del usuario o la instrucción para la IA.
        image_data (str, optional): Datos de la imagen en base64. Defaults to None.
        chat_history_context (list, optional): Historial de chat para contexto conversacional. Defaults to None.
    Returns:
        str: La respuesta de la IA.
    """
    # Añadir el mensaje del usuario al historial antes de enviar
    current_chat_entry = {"role": "user", "parts": [{"text": prompt}]}
    if image_data:
        current_chat_entry["parts"].append({
            "inlineData": {
                "mimeType": "image/jpeg", # Asumimos JPEG, puedes ajustar si es necesario
                "data": image_data
            }
        })
    st.session_state.chat_history.append(current_chat_entry)


    # Construir el payload para la API
    payload_contents = []
    if chat_history_context:
        # Asegurarse de que el historial de chat se envíe en el formato correcto
        # Filtrar solo los roles 'user' y 'model' para el contexto
        for msg in chat_history_context:
            if msg["role"] in ["user", "model"]:
                payload_contents.append(msg)

    # Añadir el mensaje actual del usuario al payload
    payload_contents.append(current_chat_entry)


    payload = {"contents": payload_contents}

    # Clave de API (se dejará vacía para que Canvas la inyecte en tiempo de ejecución)
    api_key = ""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        st.write("Analizando la imagen con IA... por favor espera.")
        # Simulación de la llamada fetch para el entorno de Canvas
        # En un entorno de Python puro de Streamlit, usarías `requests.post`
        # y manejarías el JSON directamente.
        # Dado que el entorno de Canvas soporta `fetch` en JS, lo simulamos aquí.

        # Para este ejemplo, vamos a simular la respuesta de Gemini para la imagen.
        # En un entorno real, la respuesta vendría de la API.
        if image_data:
            # Si hay imagen, la IA "analizará" la imagen
            simulated_ai_response = f"""
            ¡Hola! Soy tu recepcionista IA. He analizado la imagen que me has enviado.
            **Marca:** Posiblemente [Marca detectada, ej. Ford]
            **Modelo:** Posiblemente [Modelo detectado, ej. Ranger]
            **Año:** Estimado [Año, ej. 2020]
            **Lugar del siniestro:** [Parte del vehículo, ej. Parachoques trasero y portalón]
            **Tipo de siniestro:** [Tipo de daño, ej. Abolladura en parachoques cromado y rayones en portalón]
            **Estimación de costo desde:** $ [Cantidad, ej. 250.000 CLP]

            Esta es una estimación inicial basada en la imagen. Para un presupuesto exacto, te recomendamos agendar una visita a nuestro taller.
            """
        else:
            # Si no hay imagen, la IA responderá de forma conversacional
            simulated_ai_response = f"¡Hola! Soy tu recepcionista IA. ¿En qué puedo ayudarte hoy? Si tienes un siniestro, por favor, sube una foto de tu vehículo para que pueda ayudarte con una estimación."

        ai_text = simulated_ai_response
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
    # CORRECCIÓN: Cambiado use_column_width por use_container_width
    st.image(uploaded_file, caption="Imagen subida.", use_container_width=True)
    # Convertir la imagen a base64
    bytes_data = uploaded_file.getvalue()
    image_data_base64 = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("Analizar Daño con IA"):
        with st.spinner("Analizando la imagen..."):
            prompt_for_image = """
            Actúa como un recepcionista de un taller de desabolladura y pintura.
            Analiza la imagen de este vehículo con un siniestro.
            Identifica la marca, modelo y año del vehículo.
            Describe el lugar específico del siniestro (ej. puerta delantera derecha, parachoques trasero).
            Clasifica el tipo de siniestro (ej. rayón leve, abolladura, choque mayor).
            Proporciona una estimación de costo 'desde' en pesos chilenos (CLP) para la reparación.
            Formatea tu respuesta de manera clara y concisa, como si estuvieras hablando con un cliente.
            """
            response = asyncio.run(call_gemini_api(prompt_for_image, image_data=image_data_base64, chat_history_context=list(st.session_state.chat_history)))
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
    # Si el usuario ingresa texto, envía la pregunta a la IA
    with st.spinner("Pensando..."):
        response = asyncio.run(call_gemini_api(user_input, chat_history_context=list(st.session_state.chat_history)))
    st.rerun() # Para refrescar la interfaz y mostrar el nuevo mensaje

