import os
import asyncio
from dotenv import load_dotenv
from PIL import Image
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import time

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configuring google.generativeai with API key
genai.configure(api_key=GOOGLE_API_KEY)

# Function to load the Gemini-Pro model
def load_gemini_pro_model(model_name="gemini-pro"):
    gemini_pro_model = genai.GenerativeModel(model_name)
    return gemini_pro_model

# Function to get a response from Gemini-Pro model
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to set up input image for processing
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to upload audio file to Gemini API
def upload_audio_file(file_path):
    try:
        return genai.upload_file(path=file_path)
    except Exception as e:
        raise Exception(f"Failed to upload file: {e}")

# Function to generate transcription from an audio file
def generate_transcription(file_path):
    model = genai.GenerativeModel('gemini-1.5-flash')
    your_file = upload_audio_file(file_path)
    prompt = "Generate transcription from the audio, only extract speech and ignore background audio."
    response = model.generate_content([prompt, your_file])
    if response.parts:
        transcription = ''.join(part.text for part in response.parts)
        return transcription
    else:
        return "No transcription available."

# Function to upload video file to Gemini API
def upload_video_file(file_path):
    try:
        return genai.upload_file(path=file_path)
    except Exception as e:
        raise Exception(f"Failed to upload file: {e}")

# Function to generate transcription from a video file
def generate_video_transcription(file_path):
    model = genai.GenerativeModel('gemini-1.5-flash')
    video_file = upload_video_file(file_path)
    prompt = "Generate transcription from the video, only extract speech and ignore background audio."
    response = model.generate_content([prompt, video_file])
    if response.parts:
        transcription = ''.join(part.text for part in response.parts)
        return transcription
    else:
        return "No transcription available."

# Function to embed text content using Google Generative AI
def embed_text(content):
    result = genai.embed_content(
        model="models/embedding-001",
        content=content,
        task_type="retrieval_document",
        title="Embedding of single string"
    )
    return result

# Function to extract text from PDF files
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Function to create and save a vector store from text chunks
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Function to get the conversational chain
def get_conversational_chain():
    prompt_template = """
        You are an expert assistant with deep knowledge in various domains. When answering the question, provide comprehensive and detailed information based on the given context. 

        Instructions:
        1. First, search for the answer within the provided PDF context.
        2. If the required information is not available in the PDF context, then refer to Gemini and mention, "Answer is not available in the PDF context, but here is a reference from Gemini."

        PDF Context:
        {context}

        Question:
        {question}

        Detailed Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# Asynchronous function to handle user input and get the response
async def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = await chain.acall({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return response["output_text"]
