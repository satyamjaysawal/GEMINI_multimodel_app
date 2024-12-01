import os
import re
import requests
import logging
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from colorama import Fore, Style

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Custom logging with colorama
def log_info(message):
    logging.info(Fore.GREEN + message + Style.RESET_ALL)

def log_warning(message):
    logging.warning(Fore.YELLOW + message + Style.RESET_ALL)

def log_error(message):
    logging.error(Fore.RED + message + Style.RESET_ALL)

# Configure Google API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    log_error("Google API key not found in environment variables.")
    raise EnvironmentError("Google API key not found in environment variables.")

genai = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# URL validation function
def is_valid_url(url):
    """Check if the URL is in a valid format."""
    url_pattern = r'^(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(url_pattern, url))

# Recursive extraction function
def extract_recursive(url, visited=None, depth=1, max_depth=2):
    """
    Recursively fetch and extract text and URLs from the provided URL.
    """
    if visited is None:
        visited = set()
    if depth > max_depth or url in visited:
        return "", []
    try:
        log_info(f"Fetching URL: {url} at depth {depth}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        visited.add(url)

        # Extract text
        text = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')]).strip()
        log_info(f"Extracted text from {url}:\n{text}\n")  # Log the extracted text

        # Extract URLs
        all_urls = [a['href'] for a in soup.find_all('a', href=True) if is_valid_url(a['href'])]
        log_info(f"Found URLs on {url}:\n{all_urls}\n")  # Log the extracted URLs

        # Recursively fetch data from extracted URLs
        for link in all_urls:
            child_text, _ = extract_recursive(link, visited, depth + 1, max_depth)
            text += " " + child_text
        return text, list(visited)
    except Exception as e:
        log_error(f"Error extracting data from {url}: {e}")
        return "", []

# Text chunking
def get_text_chunks(raw_text):
    """Split raw text into manageable chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return splitter.split_text(raw_text)

# Create FAISS vector store
def get_vector_store(text_chunks):
    """Create a vector store using Google Generative AI embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Google AI embeddings
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)  # Create vector store
    vector_store.save_local("faiss_index")  # Save vector store locally
    log_info("Vector store created and saved locally.")
    return vector_store

# Generate Q&A or Summarization
def process_text_with_google_genai(vector_store, query=None, task="summarize"):
    try:
        if task == "summarize":
            # Retrieve all documents for summarization
            docs = vector_store.similarity_search("", k=10)
            text = " ".join([doc.page_content for doc in docs])
            prompt = PromptTemplate(
                input_variables=["text"],
                template="Summarize the following content: {text}"
            )
            formatted_prompt = prompt.format(text=text)
        else:  # Q&A Task
            # Retrieve chunks most relevant to the query
            docs = vector_store.similarity_search(query, k=30)  # Increased scope
            retrieved_text = " ".join([doc.page_content for doc in docs])
            
            # Log retrieved text
            log_info(f"Retrieved Text for Query '{query}':\n{retrieved_text}\n")
            
            # Filter relevant chunks based on potential product-related keywords
            keywords = ["product", "model", "car", "features", "vehicle", "EV"]
            filtered_text = " ".join(
                chunk for chunk in retrieved_text.split("\n")
                if any(keyword.lower() in chunk.lower() for keyword in keywords)
            )
            log_info(f"Filtered Text for Query '{query}':\n{filtered_text}\n")

            prompt = PromptTemplate(
                input_variables=["text", "query"],
                template="""
                Based on the following text, identify and list all products, models, or vehicles mentioned.
                Provide a summary if relevant.

                Context:
                {text}

                Question:
                {query}

                Answer in bullet points with product names and short descriptions where applicable.
                """
            )
            formatted_prompt = prompt.format(text=filtered_text, query=query)

        # Send prompt to Generative AI
        response = genai.invoke(formatted_prompt)
        log_info("Processed text with Google Generative AI successfully.")
        return response.content if hasattr(response, "content") else "No response content found."
    except Exception as e:
        log_error(f"Error processing text with Google Gemini AI: {e}")
        return str(e)


# Home route
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>URL Analysis</title>
        </head>
        <body>
            <h1>Analyze URL Content</h1>
            <form action="/process" method="POST">
                <label for="url">Enter URL:</label>
                <input type="text" id="url" name="url" required>
                <label for="task">Select Task:</label>
                <select id="task" name="task">
                    <option value="summarize">URL Summarization</option>
                    <option value="qa">Q&A from URL</option>
                </select>
                <label for="query" id="query-label" style="display: none;">Enter Question:</label>
                <input type="text" id="query" name="query" style="display: none;">
                <button type="submit">Submit</button>
            </form>
            <script>
                document.getElementById('task').addEventListener('change', function() {
                    const queryField = document.getElementById('query');
                    const queryLabel = document.getElementById('query-label');
                    if (this.value === 'qa') {
                        queryField.style.display = 'block';
                        queryLabel.style.display = 'block';
                    } else {
                        queryField.style.display = 'none';
                        queryLabel.style.display = 'none';
                    }
                });
            </script>
        </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url')
    task = request.form.get('task')
    query = request.form.get('query') if task == "qa" else None
    
    if not is_valid_url(url):
        log_warning("Invalid URL format provided.")
        return "Invalid URL format", 400
    
    # Extract data recursively
    log_info(f"Starting extraction for URL: {url}")
    aggregated_text, visited_urls = extract_recursive(url)
    if not aggregated_text:
        log_error("No data found or error during extraction.")
        return "Error extracting data or no data found.", 500
    
    # Print complete extracted text to the terminal
    log_info(f"Complete Extracted Text:\n{aggregated_text}\n")
    
    # Process extracted text into chunks and vector store
    log_info("Splitting text into chunks and creating vector store.")
    text_chunks = get_text_chunks(aggregated_text)
    vector_store = get_vector_store(text_chunks)
    
    # Process the task
    log_info(f"Task selected: {task}")
    if task == "summarize":
        result = process_text_with_google_genai(vector_store)
        log_info(f"Processed Summarization Result:\n{result}")
    elif task == "qa":
        log_info(f"User Query: {query}")
        result = process_text_with_google_genai(vector_store, query=query, task="qa")
        log_info(f"Processed Q&A Result:\n{result}")
    
    # Render the result
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>URL Analysis Result</title>
        </head>
        <body>
            <h1>Results</h1>
            <h2>Visited URLs</h2>
            <ul>
                {% for u in visited_urls %}
                    <li>{{ u }}</li>
                {% endfor %}
            </ul>
            <h2>Processed Result</h2>
            <p>{{ result }}</p>
            <a href="/">Go Back</a>
        </body>
    </html>
    ''', visited_urls=visited_urls, result=result)


if __name__ == '__main__':
    app.run(debug=True)
