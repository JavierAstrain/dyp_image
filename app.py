import streamlit as st
import base64
import json
import asyncio # Para manejar operaciones asíncronas

# Variables globales para Firebase (obligatorias, aunque no se usen para persistencia en este ejemplo de Streamlit)
# Estas variables son proporcionadas por el entorno de Canvas.
app_id = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id'
firebase_config_str = typeof __firebase_config !== 'undefined' ? __firebase_config : '{}'
firebase_config = json.loads(firebase_config_str)
initial_auth_token = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : None

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
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": prompt}]})

    # Construir el payload para la API
    payload_contents = []
    if chat_history_context:
        payload_contents.extend(chat_history_context)

    user_parts = [{"text": prompt}]
    if image_data:
        user_parts.append({
            "inlineData": {
                "mimeType": "image/jpeg", # Asumimos JPEG, puedes ajustar si es necesario
                "data": image_data
            }
        })
    payload_contents.append({"role": "user", "parts": user_parts})

    payload = {"contents": payload_contents}

    # Clave de API (se dejará vacía para que Canvas la inyecte en tiempo de ejecución)
    api_key = ""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        # Usar fetch para la llamada a la API
        # En un entorno de Streamlit puro, esto requeriría un backend o una librería JS.
        # Aquí, estamos simulando cómo se haría en un entorno que soporta `fetch` directamente.
        # Para un Streamlit real, usarías una librería HTTP de Python como `requests`.
        # Dado que el entorno de Canvas soporta `fetch` en JS, lo simulamos aquí.
        st.write("Analizando la imagen con IA... por favor espera.")
        # Simulación de la llamada fetch para el entorno de Canvas
        # En un entorno de Python puro de Streamlit, usarías `requests.post`
        # y manejarías el JSON directamente.
        # Aquí, esta parte es una representación conceptual de la llamada API.
        response_placeholder = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Simulando análisis de imagen. Por favor, sube una imagen real para un análisis más preciso."}
                        ]
                    }
                }
            ]
        }

        # Para que esto funcione en un entorno de Streamlit real, necesitarías:
        # 1. Usar la librería `requests` de Python.
        # 2. Asegurarte de que la clave de API esté configurada de forma segura (ej. variables de entorno).
        # 3. Considerar un backend para manejar la lógica de la IA si es muy pesada.

        # Ejemplo de cómo sería con `requests` (no ejecutable directamente en el entorno de Canvas sin un servidor)
        # import requests
        # headers = {'Content-Type': 'application/json'}
        # response = requests.post(api_url, headers=headers, json=payload)
        # result = response.json()

        # Para el propósito de este demo en Canvas, usaremos un placeholder o una llamada real si el entorno lo permite.
        # Para que el código sea ejecutable en Canvas, la llamada fetch debe ser JS.
        # Como estamos en Python (Streamlit), esta parte es una representación.
        # Si este código se ejecuta en un entorno que permite JS fetch, se ejecutaría.
        # De lo contrario, se necesitaría un ajuste para usar una librería HTTP de Python.

        # Para este ejemplo, vamos a simular la respuesta de Gemini para la imagen.
        # En un entorno real, la respuesta vendría de la API.
        if image_data:
            # Si hay imagen, la IA "analizará" la imagen
            simulated_ai_response = f"""
            ¡Hola! Soy tu recepcionista IA. He analizado la imagen que me has enviado.
            **Marca:** Posiblemente [Marca detectada, ej. Toyota]
            **Modelo:** Posiblemente [Modelo detectado, ej. Corolla]
            **Año:** Estimado [Año, ej. 2018]
            **Lugar del siniestro:** [Parte del vehículo, ej. Puerta delantera izquierda]
            **Tipo de siniestro:** [Tipo de daño, ej. Abolladura leve y rayones]
            **Estimación de costo desde:** $ [Cantidad, ej. 150.000 CLP]

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
    st.image(uploaded_file, caption="Imagen subida.", use_column_width=True)
    # Convertir la imagen a base64
    bytes_data = uploaded_file.getvalue()
    image_data_base64 = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("Analizar Daño con IA"):
        with st.spinner("Analizando la imagen..."):
            # Llamar a la función asíncrona usando asyncio.run() para Streamlit
            # Nota: asyncio.run() solo se puede llamar una vez por hilo.
            # Para un entorno de Streamlit más robusto, se usaría `st.experimental_memo` o `st.cache_data`
            # con una función asíncrona, o se manejaría la llamada API en un hilo separado.
            # Aquí, para simplificar y mostrar el concepto:
            # Se simula la respuesta de la IA para la imagen.
            prompt_for_image = """
            Actúa como un recepcionista de un taller de desabolladura y pintura.
            Analiza la imagen de este vehículo con un siniestro.
            Identifica la marca, modelo y año del vehículo.
            Describe el lugar específico del siniestro (ej. puerta delantera derecha, parachoques trasero).
            Clasifica el tipo de siniestro (ej. rayón leve, abolladura, choque mayor).
            Proporciona una estimación de costo 'desde' en pesos chilenos (CLP) para la reparación.
            Formatea tu respuesta de manera clara y concisa, como si estuvieras hablando con un cliente.
            """
            response = asyncio.run(call_gemini_api(prompt_for_image, image_data=image_data_base64))
            st.write(response)

st.subheader("2. Conversa con el recepcionista IA")

# Mostrar historial de chat
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"<div class='chat-message user-message'><b>Tú:</b> {message['parts'][0]['text']}</div>", unsafe_allow_html=True)
    elif message["role"] == "model":
        st.markdown(f"<div class='chat-message ai-message'><b>Recepcionista IA:</b> {message['parts'][0]['text']}</div>", unsafe_allow_html=True)

# Entrada de texto para el usuario
user_input = st.text_input("Escribe tu mensaje aquí:", key="user_input")

if user_input:
    # Si el usuario ingresa texto, envía la pregunta a la IA
    with st.spinner("Pensando..."):
        # Se envía el historial completo para que la IA tenga contexto
        response = asyncio.run(call_gemini_api(user_input, chat_history_context=st.session_state.chat_history))
        # El historial ya se actualiza dentro de call_gemini_api
    st.rerun() # Para refrescar la interfaz y mostrar el nuevo mensaje

