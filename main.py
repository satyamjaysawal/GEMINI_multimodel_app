import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import asyncio
from streamlit_option_menu import option_menu
from gemini_utility import load_gemini_pro_model, get_gemini_response, embed_text, get_pdf_text, get_text_chunks, get_vector_store, user_input
from gemini_utility import upload_audio_file, generate_transcription

from gemini_utility import load_gemini_pro_model, generate_video_transcription
import tempfile
from gemini_utility import input_image_setup
from playsound import playsound
# Import additional libraries for voice assistance
import speech_recognition as sr
from gtts import gTTS
#import pyaudio

# Load environment variables from .env file
load_dotenv()

# Setting up the page configuration
st.set_page_config(
    page_title="Gemini AI",
    page_icon="🤖",
    layout="centered"
)

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Gemini AI",
        options=["ChatBot", "Image Captioning", "Embed Text", "Chat with PDF", "Voice Assistant", "Transcribe Audio", "Transcribe Video"],
        icons=['chat-dots', 'image', 'textarea-t', 'file-earmark-pdf', 'mic', 'file-music', 'film'],
        default_index=0
    )

# Function to translate user roles for Streamlit chat display
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# ChatBot section
if selected == "ChatBot":
    model = load_gemini_pro_model()

    # Initialize chat session in Streamlit if not already present
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("ChatBot")
    # Display the chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask Gemini-Pro...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        gemini_response = st.session_state.chat_session.send_message(user_prompt)

        # Display Gemini-Pro response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

# Image Captioning section
elif selected == "Image Captioning":
    st.title("Gemini Image Captioning")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    input = st.text_input("Input Prompt: ", key="input")
    submit = st.button("Generate Text")

    input_prompt = """
        You are an advanced AI specialized in image understanding. Analyze the provided image and offer a detailed description. Address the following points in separate sections:

        1. **Main Subjects/Objects**:
        Identify and describe the primary subjects or objects in the image.

        2. **Notable Actions/Activities**:
        Describe any significant actions or activities occurring in the image.

        3. **Background Elements/Scenery**:
        Highlight important background elements or scenery details.

        4. **Specific Details**:
        Note any specific details such as colors, textures, patterns, or expressions.

        5. **Overall Context/Scenario**:
        Provide an overall context or possible scenario depicted in the image.

        Image description:
    """


    # If submit button is clicked
    if submit:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input)
        st.subheader("The Response is")
        st.write(response)

# Embed Text section
elif selected == "Embed Text":
    st.title("Embed Text")
    text_to_embed = st.text_area("Enter text to embed:")

    if st.button("Generate Embedding"):
        if text_to_embed:
            embedding_result = embed_text(text_to_embed)
            st.write("Embedding Result:")
            st.json(embedding_result)

# Chat with PDF section
elif selected == "Chat with PDF":
    st.title("Chat with PDF using Gemini💁")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        response = asyncio.run(user_input(user_question))
        st.write("Reply:", response)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

# Voice Assistant section
elif selected == "Voice Assistant":
    st.title("Gemini AI Voice Assistant")
    st.write("Click the button below and speak to get a response from Gemini.")

    if st.button("Speak Now"):
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            st.write("Listening...")
            audio = r.listen(source)
        try:
            # Recognize the speech using Google's speech recognition
            text = r.recognize_google(audio)
            st.write(f"You said: {text}")

            # Generate content using the generative model
            model = load_gemini_pro_model()
            response = model.generate_content(text)
            response_text = response.text
            st.write(f"Gemini response: {response_text}")

            # Convert the response text to speech
            tts = gTTS(response_text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                audio_file = fp.name

            # Play the generated speech audio using playsound
            st.audio(audio_file)

        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            st.write(f"An error occurred: {e}")

# Transcribe Audio section
elif selected == "Transcribe Audio":
    st.title("Transcribe Audio")
    uploaded_file = st.file_uploader("Choose an MP3 file...", type=["mp3"])

    if uploaded_file is not None:
        with st.spinner("Transcribing..."):
            try:
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(uploaded_file.read())
                    file_path = temp_file.name

                # Play the uploaded audio file
                st.audio(file_path)

                # Upload the audio file and generate transcription
                transcription = generate_transcription(file_path)

                st.subheader("Transcription")
                st.write(transcription)

            except Exception as e:
                st.error(f"Error: {e}")

# Transcribe Video section
elif selected == "Transcribe Video":
    st.title("Transcribe Video")
    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            try:
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    temp_file.write(uploaded_file.read())
                    file_path = temp_file.name

                # Play the uploaded video file
                st.video(file_path)

                # Upload the video file and generate transcription
                transcription = generate_video_transcription(file_path)

                st.subheader("Transcription")
                st.write(transcription)

            except Exception as e:
                st.error(f"Error: {e}")
