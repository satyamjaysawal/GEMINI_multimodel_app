import os
import re
import requests
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Load environment variables
print("Loading environment variables...")
load_dotenv()

app = Flask(__name__)

# Configure Google API key from the .env file
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise EnvironmentError("Google API key not found in environment variables.")
print("Google API key loaded successfully.")
genai.configure(api_key=google_api_key)

# URL validation function
def is_valid_url(url):
    """Check if the URL is in a valid format."""
    print(f"Validating URL format: {url}")
    url_pattern = r'^(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    valid = bool(re.match(url_pattern, url))
    print(f"URL valid: {valid}")
    return valid

# Function to extract text from the URL
def extract_text_from_url(url):
    """Fetch and extract text from the URL."""
    print(f"Fetching and extracting text from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check if the response status is OK (200)
        print("Response received successfully from URL.")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        
        if not paragraphs:
            print("No paragraphs found in <p> tags.")
            return None, "No meaningful text found in <p> tags on the page."
        
        text = ' '.join(paragraphs).strip()
        if not text:
            print("Extracted text is empty.")
            return None, "Extracted text is empty or non-meaningful."
        
        print("Text extracted successfully.")
        return text, None
    except requests.exceptions.Timeout:
        print("Request to URL timed out.")
        return None, "The request timed out while trying to fetch the URL."
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None, f"Request failed: {str(e)}"


# Function to process text using Google Generative AI
def process_text_with_google_genai(text):
    """Summarize text using Google Generative AI."""
    print("Processing text with Google Generative AI...")
    try:
        # Initialize the Google Generative AI model using langchain integration
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        # prompt = PromptTemplate(input_variables=["text"], template="Summarize this article: {text}")
        prompt = PromptTemplate(
            input_variables=["text"], 
            template="""
                Summarize the main insights from the article provided below. Include:
                
                - An overview of the main arguments or ideas.
                - Important data or evidence presented.
                - Practical implications or recommendations, if available.
                
                Article content: {text}
            """
        )


        
        # Generate a summary from the extracted text
        response = model.invoke(prompt.format(text=text))
        
        # Assuming response is an AIMessage object, access its content
        if hasattr(response, 'content'):
            summary = response.content  # Adjust based on actual attribute name
        else:
            print("Error: Response object does not have 'content' attribute.")
            return None, "Invalid response format from Google Generative AI."

        # Check if summary text is valid
        if not summary or not summary.strip():
            print("Google Generative AI returned an empty response.")
            return None, "Google Generative AI returned an empty response."
        
        print("Text processed successfully by Google Generative AI.")
        return summary, None
    except Exception as e:
        print(f"Google Generative AI processing failed: {str(e)}")
        return None, f"Google Generative AI processing failed: {str(e)}"


# Home route (render the input form)
@app.route('/')
def index():
    print("Rendering home page with input form.")
    return '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>URL Text Extraction & Processing</title>
                <!-- Bootstrap CSS -->
                <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container mt-5">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h2 class="mb-0">Extract and Process Text from a URL</h2>
                        </div>
                        <div class="card-body">
                            <form action="/extract_and_process" method="POST">
                                <div class="form-group">
                                    <label for="url">Enter URL:</label>
                                    <input type="text" class="form-control" id="url" name="url" placeholder="https://example.com" required>
                                </div>
                                <button type="submit" class="btn btn-success">Submit</button>
                            </form>
                        </div>
                        <div class="card-footer text-muted">
                            <p>Instructions:</p>
                            <ul>
                                <li>Enter a valid URL (including http:// or https://).</li>
                                <li>Click Submit to fetch and process the content from the URL.</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <!-- Bootstrap JS and dependencies -->
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js"></script>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
        </html>
    '''

@app.route('/extract_and_process', methods=['POST'])
def extract_and_process():
    print("Received POST request at /extract_and_process")
    data = request.form
    url = data.get('url')
    if not url:
        return '''<html><body><h1>Error</h1><p>URL is required.</p></body></html>''', 400
    if not is_valid_url(url):
        return '''<html><body><h1>Error</h1><p>Invalid URL format. Ensure it includes http:// or https://</p></body></html>''', 400

    print("Starting text extraction...")
    text, error = extract_text_from_url(url)
    if error:
        return f'''<html><body><h1>Error</h1><p>{error}</p></body></html>''', 500

    print("Starting text processing with Google Generative AI...")
    processed_text, error = process_text_with_google_genai(text)
    if error:
        return f'''<html><body><h1>Error</h1><p>{error}</p></body></html>''', 500

    print("Rendering result page with extracted and processed text.")
    return render_template_string(f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Extracted and Processed Text</title>
                <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{
                        background-color: #f8f9fa;
                    }}
                    .content-container {{
                        margin-top: 50px;
                    }}
                    .card {{
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        border: none;
                    }}
                    .header {{
                        background-color: #007bff;
                        color: #fff;
                    }}
                    .section-title {{
                        font-weight: bold;
                        color: #007bff;
                    }}
                    .text-block {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        border: 1px solid #e0e0e0;
                        margin-bottom: 20px;
                        white-space: pre-wrap;  /* Preserve line breaks and spacing */
                    }}
                    .btn-primary {{
                        background-color: #007bff;
                        border-color: #007bff;
                    }}
                </style>
            </head>
            <body>
                <div class="container content-container">
                    <div class="card">
                        <div class="card-header header">
                            <h2 class="mb-0">Extracted and Processed Text</h2>
                        </div>
                        <div class="card-body">
                            <div class="mb-4">
                                <h4 class="section-title">Extracted Text</h4>
                                <div class="text-block">
                                    <p>{text}</p>
                                </div>
                            </div>
                            <div>
                                <h4 class="section-title">Processed Text (Summary)</h4>
                                <div class="text-block">
                                    <p>{processed_text}</p>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer text-right">
                            <a href="/" class="btn btn-primary">Go Back</a>
                        </div>
                    </div>
                </div>
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js"></script>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
        </html>
    ''')



if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)
