

![image](https://github.com/user-attachments/assets/b23a5f41-9cd2-4f13-80f9-00b71fdf050c)
![image](https://github.com/user-attachments/assets/cd16e47d-72c2-40c1-993b-13034d30bb9d)


****

```python
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import faiss
import numpy as np
from urllib.parse import urlparse
from colorama import Fore, Style
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure Google Generative AI API
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Global variables to track state
last_processed_url = None
chunks = None  # Store chunks of text for the last processed URL

# Function to validate URL
def is_valid_url(url):
    """Checks if a given URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Function to fetch and extract text from a URL
# def extract_text_from_url(url):
#     """Fetches and extracts text content from a URL."""
#     print(Fore.YELLOW + "Validating URL..." + Style.RESET_ALL)
#     if not is_valid_url(url):
#         print(Fore.RED + "Invalid URL provided. Exiting." + Style.RESET_ALL)
#         raise ValueError("Invalid URL provided.")
#     try:
#         print(Fore.YELLOW + "Fetching content from URL..." + Style.RESET_ALL)
#         response = requests.get(url, verify=False)  # Disable SSL verification
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
#         print(Fore.GREEN + "Content fetched successfully!" + Style.RESET_ALL)
#         return "\n".join(soup.stripped_strings)
#     except requests.exceptions.RequestException as e:
#         print(Fore.RED + f"Failed to fetch URL content: {e}" + Style.RESET_ALL)
#         raise RuntimeError(f"Failed to fetch URL content: {e}")

# def extract_text_from_url(url, depth=1, max_depth=3, visited=None):
#     """Fetches and extracts text content from a URL and follows links recursively up to a specified depth."""
#     if visited is None:
#         visited = set()  # Keep track of visited URLs to avoid revisiting
#     if depth > max_depth:
#         return ""

#     if url in visited:
#         print(Fore.BLUE + f"URL already visited: {url}" + Style.RESET_ALL)
#         return ""
    
#     visited.add(url)
#     print(Fore.YELLOW + f"Depth {depth}: Fetching content from URL: {url}" + Style.RESET_ALL)

#     try:
#         response = requests.get(url, verify=False, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Extract text from the current page
#         page_text = "\n".join(soup.stripped_strings)
        
#         # Recursively fetch links on the page
#         if depth < max_depth:
#             print(Fore.YELLOW + f"Depth {depth}: Extracting links from: {url}" + Style.RESET_ALL)
#             links = {link.get('href') for link in soup.find_all('a', href=True)}
#             links = {link for link in links if is_valid_url(link)}  # Only process valid URLs
#             for link in links:
#                 page_text += "\n" + extract_text_from_url(link, depth + 1, max_depth, visited)

#         print(Fore.GREEN + f"Depth {depth}: Content fetched successfully from: {url}" + Style.RESET_ALL)
#         return page_text

#     except requests.exceptions.RequestException as e:
#         print(Fore.RED + f"Failed to fetch URL content: {e}" + Style.RESET_ALL)
#         return ""


import time

def extract_text_from_url(url, depth=1, max_depth=3, visited=None, start_time=None, time_limit=60):
    """
    Fetches and extracts text content from a URL and follows links recursively up to a specified depth,
    with a time constraint.
    """
    if visited is None:
        visited = set()  # Keep track of visited URLs to avoid revisiting
    if start_time is None:
        start_time = time.time()

    if depth > max_depth:
        return ""
    if time.time() - start_time > time_limit:
        print(Fore.RED + "Time limit reached. Stopping extraction." + Style.RESET_ALL)
        return ""

    if url in visited:
        print(Fore.BLUE + f"URL already visited: {url}" + Style.RESET_ALL)
        return ""
    
    visited.add(url)
    print(Fore.YELLOW + f"Depth {depth}: Fetching content from URL: {url}" + Style.RESET_ALL)

    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from the current page
        page_text = "\n".join(soup.stripped_strings)
        
        # Recursively fetch links on the page
        if depth < max_depth:
            print(Fore.YELLOW + f"Depth {depth}: Extracting links from: {url}" + Style.RESET_ALL)
            links = {link.get('href') for link in soup.find_all('a', href=True)}
            links = {link for link in links if is_valid_url(link)}  # Only process valid URLs
            for link in links:
                if time.time() - start_time > time_limit:
                    print(Fore.RED + "Time limit reached during link extraction. Stopping." + Style.RESET_ALL)
                    break
                page_text += "\n" + extract_text_from_url(
                    link, depth + 1, max_depth, visited, start_time, time_limit
                )

        print(Fore.GREEN + f"Depth {depth}: Content fetched successfully from: {url}" + Style.RESET_ALL)
        return page_text

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to fetch URL content: {e}" + Style.RESET_ALL)
        return ""



# Function to save text to a file
def save_text_to_file(text, filename):
    """Saves text content to a file."""
    print(Fore.YELLOW + f"Saving extracted text to file: {filename}" + Style.RESET_ALL)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    print(Fore.GREEN + "Text saved successfully!" + Style.RESET_ALL)

# Function to split text into smaller chunks
def split_text_into_chunks(text, max_chunk_size=5000):
    """Splits text into smaller chunks for embedding."""
    print(Fore.YELLOW + "Splitting text into smaller chunks..." + Style.RESET_ALL)
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

    print(Fore.GREEN + f"Text split into {len(chunks)} chunks." + Style.RESET_ALL)
    return chunks

# Function to generate embeddings using Google's Generative AI
def generate_google_embedding(text):
    """Generates embedding for a given text."""
    print(Fore.YELLOW + "Generating embedding for text chunk..." + Style.RESET_ALL)
    try:
        response = genai.embed_content(
            model="models/embedding-001", content=text, task_type="retrieval_document"
        )
        print(Fore.GREEN + "Embedding generated successfully!" + Style.RESET_ALL)
        return np.array(response['embedding']).astype('float32')
    except Exception as e:
        print(Fore.RED + f"Error generating embedding: {e}" + Style.RESET_ALL)
        raise RuntimeError(f"Error generating embedding: {e}")

# Function to create and save FAISS index
def create_faiss_index(text, index_filename="faiss_index"):
    """Creates and saves a FAISS index from the given text."""
    print(Fore.YELLOW + "Creating FAISS index..." + Style.RESET_ALL)
    global chunks
    chunks = split_text_into_chunks(text)
    embeddings = []

    for chunk in chunks:
        embedding = generate_google_embedding(chunk)
        embeddings.append(embedding)

    embeddings_array = np.vstack(embeddings)
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)
    faiss.write_index(index, index_filename)
    print(Fore.GREEN + "FAISS index created and saved successfully!" + Style.RESET_ALL)
    return chunks

# Function to load FAISS index
def load_faiss_index(index_filename="faiss_index"):
    """Loads a FAISS index from a file."""
    print(Fore.YELLOW + f"Loading FAISS index from file: {index_filename}" + Style.RESET_ALL)
    if not os.path.exists(index_filename):
        print(Fore.RED + f"FAISS index file {index_filename} not found!" + Style.RESET_ALL)
        raise FileNotFoundError(f"FAISS index file {index_filename} not found.")
    print(Fore.GREEN + "FAISS index loaded successfully!" + Style.RESET_ALL)
    return faiss.read_index(index_filename)

# Function to perform similarity search
def similarity_search(query, index_filename="faiss_index", k=5):
    """Performs similarity search on the FAISS index and retrieves top-k results."""
    print(Fore.YELLOW + f"Performing similarity search with top {k} results..." + Style.RESET_ALL)
    query_embedding = generate_google_embedding(query)
    index = load_faiss_index(index_filename)
    distances, indices = index.search(np.array([query_embedding]), k)
    print(Fore.GREEN + "Similarity search completed!" + Style.RESET_ALL)
    return distances[0], indices[0]

# Main function
def main():
    global last_processed_url, chunks  # Access global variables

    while True:  # Keep running until the user decides to exit
        print(Fore.CYAN + "\nWelcome to the AI Content Finder!" + Style.RESET_ALL)
        print("Choose an option:")
        print("1. Enter URL and query")
        print("2. Exit the application")

        choice = input(Fore.YELLOW + "\nEnter your choice (1 or 2): " + Style.RESET_ALL)

        if choice == "1":
            url = input("\nEnter the URL: ")

            if url == last_processed_url:
                print(Fore.BLUE + "Reusing previously processed URL and FAISS index..." + Style.RESET_ALL)
            else:
                print(Fore.BLUE + "Processing the URL..." + Style.RESET_ALL)
                try:
                    text = extract_text_from_url(url)
                    save_text_to_file(text, "extracted_text.txt")
                    create_faiss_index(text)
                    last_processed_url = url
                except Exception as e:
                    print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
                    continue

            query = input("Enter your query: ")

            # Process the query
            try:
                distances, indices = similarity_search(query, k=5)
                combined_context = "\n\n".join(chunks[idx] for idx in indices)
                print(Fore.BLUE + "Generating concise summary..." + Style.RESET_ALL)
                response = model.generate_content([
                    f"Context: {combined_context}\n\nQuestion: {query}\n\nSummarize in detail:"
                ])
                print(Fore.GREEN + f"Answer: {response.text}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"An error occurred during similarity search or summarization: {e}" + Style.RESET_ALL)

            # Allow additional queries
            while True:
                print(Fore.CYAN + "\nQuerying from the current URL..." + Style.RESET_ALL)
                print("1. Enter another query")
                print("2. Exit to process a new URL")
                query_choice = input(Fore.YELLOW + "\nEnter your choice (1 or 2): " + Style.RESET_ALL)

                if query_choice == "1":
                    query = input("Enter your query: ")
                    try:
                        distances, indices = similarity_search(query, k=5)
                        combined_context = "\n\n".join(chunks[idx] for idx in indices)
                        print(Fore.BLUE + "Generating concise summary..." + Style.RESET_ALL)
                        response = model.generate_content([
                            f"Context: {combined_context}\n\nQuestion: {query}\n\nSummarize in detail:"
                        ])
                        print(Fore.GREEN + f"Answer: {response.text}" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"An error occurred during similarity search or summarization: {e}" + Style.RESET_ALL)

                elif query_choice == "2":
                    print(Fore.BLUE + "Exiting to process a new URL..." + Style.RESET_ALL)
                    break

                else:
                    print(Fore.RED + "Invalid choice. Please enter 1 or 2." + Style.RESET_ALL)

        elif choice == "2":
            print(Fore.GREEN + "\nThank you for using the AI Content Finder. Goodbye!" + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "Invalid choice. Please enter 1 or 2." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
```

---

# AI Content Finder (CLI Version)

A command-line tool that extracts content from a given URL, indexes it using FAISS for similarity searches, and provides summarized answers to user queries using Google's Generative AI.

---

## Features

- **URL Content Extraction**: Extracts text content from any valid URL.
- **FAISS Indexing**: Efficient similarity search using FAISS with Google Generative AI embeddings.
- **Query and Summarization**: Allows detailed questions and provides concise answers based on extracted content.
- **Interactive CLI**: Intuitive terminal-based interface with options for repeated queries.

---

## Requirements

### Python Version
- Python 3.8 or higher

### Dependencies
Install the following Python libraries:
- `google-generativeai`
- `faiss`
- `numpy`
- `requests`
- `bs4` (BeautifulSoup)
- `colorama`
- `urllib3`

To install all dependencies, use the `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-content-finder-cli.git
   cd ai-content-finder-cli
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Google Generative AI API Key**
   - Obtain an API key from Google Generative AI.
   - Replace the placeholder in the script:
     ```python
     GOOGLE_API_KEY = "your_api_key_here"
     ```

4. **Run the Script**
   ```bash
   python main.py
   ```

---

## How to Use

1. **Start the Script**
   - Run `python main.py` in your terminal.
   - You'll be presented with an interactive menu.

2. **Process a URL**
   - Select option `1` and provide a valid URL.
   - The script fetches and extracts content from the URL.

3. **Ask Questions**
   - Enter a query to find relevant information in the content.
   - The tool will summarize the most relevant content.

4. **Re-use or Process Another URL**
   - Option to ask further questions on the same URL or process a new one.

5. **Exit**
   - Select option `2` to exit the script.

---

## Notes

- **SSL Warnings**: SSL verification is disabled to handle websites with invalid certificates. Ensure you trust the URLs you're using.
- **Text Chunking**: The content is split into manageable chunks to meet embedding size limits (5,000 tokens per chunk).
- **Index File**: FAISS indices are saved and reused for efficiency.

---

## Example Run

```plaintext
Welcome to the AI Content Finder!
Choose an option:
1. Enter URL and query
2. Exit the application

Enter your choice (1 or 2): 1

Enter the URL: https://example.com
Validating URL...
Fetching content from URL...
Content fetched successfully!
Saving extracted text to file: extracted_text.txt
Creating FAISS index...
Text split into 5 chunks.
FAISS index created and saved successfully!

Enter your query: What is the main topic of the article?
Performing similarity search with top 5 results...
Generating concise summary...
Answer: The main topic of the article is...
```

---

## Troubleshooting

### Common Issues
1. **Invalid URL**: Ensure the URL starts with `http://` or `https://`.
2. **Missing API Key**: Verify that your Google Generative AI API key is correctly set.
3. **Index File Not Found**: Ensure the FAISS index file is created before querying.

---
****
