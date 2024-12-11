Here is the complete Python code as you requested:

```python
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import faiss
import numpy as np
from urllib.parse import urlparse
import urllib3
import streamlit as st

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure Google Generative AI API
GOOGLE_API_KEY = "AIzaSyCq6fkWlTcWfWYaPAfer1nFhOiQuof1c4M"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to validate URL
def is_valid_url(url):
    """Checks if a given URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Function to fetch and extract text from a URL
def extract_text_from_url(url):
    """Fetches and extracts text content from a URL."""
    if not is_valid_url(url):
        raise ValueError("Invalid URL provided.")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return "\n".join(soup.stripped_strings)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch URL content: {e}")

# Function to split text into smaller chunks
def split_text_into_chunks(text, max_chunk_size=5000):
    """Splits text into smaller chunks for embedding."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        if current_size + len(word) + 1 <= max_chunk_size:
            current_chunk.append(word)
            current_size += len(word) + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to generate embeddings using Google's Generative AI
def generate_google_embedding(text):
    """Generates embedding for a given text."""
    try:
        response = genai.embed_content(
            model="models/embedding-001", content=text, task_type="retrieval_document"
        )
        return np.array(response['embedding']).astype('float32')
    except Exception as e:
        raise RuntimeError(f"Error generating embedding: {e}")

# Function to create and save FAISS index
def create_faiss_index(text):
    """Creates and saves a FAISS index from the given text."""
    chunks = split_text_into_chunks(text)
    embeddings = [generate_google_embedding(chunk) for chunk in chunks]
    embeddings_array = np.vstack(embeddings)
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)
    return index, chunks

# Function to perform similarity search
def similarity_search(query, index, chunks, k=5):
    """Performs similarity search on the FAISS index and retrieves top-k results."""
    query_embedding = generate_google_embedding(query)
    distances, indices = index.search(np.array([query_embedding]), k)
    return [chunks[idx] for idx in indices[0]], distances[0]

# Streamlit App
st.title("AI Content Finder")

# State management
if "last_processed_url" not in st.session_state:
    st.session_state.last_processed_url = None
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None

# URL Input
url = st.text_input("Enter a URL to process:")
if st.button("Process URL"):
    try:
        if url == st.session_state.last_processed_url:
            st.info("Reusing previously processed URL and FAISS index.")
        else:
            text = extract_text_from_url(url)
            st.session_state.faiss_index, st.session_state.chunks = create_faiss_index(text)
            st.session_state.last_processed_url = url
            st.success("URL processed successfully and FAISS index created.")
    except Exception as e:
        st.error(f"Error processing URL: {e}")

# Query Input
query = st.text_input("Enter your query:")
if st.button("Search and Summarize"):
    try:
        if st.session_state.faiss_index is None or st.session_state.chunks is None:
            st.error("No FAISS index available. Please process a URL first.")
        else:
            results, distances = similarity_search(query, st.session_state.faiss_index, st.session_state.chunks)
            combined_context = "\n\n".join(results)
            response = model.generate_content([
                f"Context: {combined_context}\n\nQuestion: {query}\n\nSummarize in detail:"
            ])
            st.markdown(f"**Answer:** {response.text}")
    except Exception as e:
        st.error(f"Error during search or summarization: {e}")
```
****
# AI Content Finder

This project is a web application that extracts content from a given URL, indexes the content using FAISS, and allows users to search and summarize relevant information using Google's Generative AI. The app is built with Streamlit.

---

## Features

- **URL Content Extraction**: Extracts text from any valid URL.
- **FAISS Indexing**: Creates an index for efficient similarity search.
- **Query and Summarization**: Searches indexed content and summarizes relevant results using Google's Generative AI.
- **Interactive UI**: User-friendly interface with Streamlit.

---

## Requirements

### Python Version
- Python 3.8 or above

### Dependencies
Install the following Python libraries:
- `streamlit`
- `requests`
- `bs4` (BeautifulSoup)
- `faiss`
- `numpy`
- `google-generativeai`
- `urllib3`

You can install all dependencies using the `requirements.txt` file.

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-content-finder.git
   cd ai-content-finder
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Google Generative AI API Key**
   - Obtain an API key from Google Generative AI.
   - Replace the placeholder `GOOGLE_API_KEY` in the code with your API key.

4. **Run the App**
   ```bash
   streamlit run app.py
   ```

---

## Usage

### Step 1: Enter a URL
1. Paste a valid URL into the input field.
2. Click **Process URL**. The app will fetch and index the content from the URL.

### Step 2: Enter a Query
1. Enter a search query related to the content of the URL.
2. Click **Search and Summarize**. The app will perform a similarity search and summarize the most relevant content.

---

## Notes
- **SSL Warnings**: SSL warnings are suppressed in this project to handle some websites with invalid certificates. Ensure you understand the risks of disabling SSL verification.
- **Embedding Limitations**: The Google Generative AI embedding model has a maximum text length limit (e.g., 5,000 tokens per chunk).

---

## Deployment

1. **Local Deployment**
   - Follow the steps in the **Installation** section to deploy the app locally.

2. **Cloud Deployment**
   - Use services like **Streamlit Cloud**, **Heroku**, or **AWS EC2** to deploy the app online.

3. **Docker Deployment (Optional)**
   - Create a Dockerfile to containerize the application:
     ```dockerfile
     FROM python:3.8-slim
     WORKDIR /app
     COPY . .
     RUN pip install -r requirements.txt
     CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
     ```
   - Build and run the Docker image:
     ```bash
     docker build -t ai-content-finder .
     docker run -p 8501:8501 ai-content-finder
     ```

---

## Troubleshooting

### Common Issues
1. **Invalid URL**:
   - Ensure the URL starts with `http://` or `https://`.

2. **API Key Errors**:
   - Verify your Google Generative AI API key is correctly set.

3. **Dependencies Missing**:
   - Double-check that all libraries in `requirements.txt` are installed.

---




****
****
