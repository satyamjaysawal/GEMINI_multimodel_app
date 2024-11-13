
---

Below is the `README.md` file for your PDF document comparison project.

---

# PDF Document Comparison with AI

This project is a web-based application built with Flask that allows users to compare the contents of two PDF documents using AI-powered insights. The app extracts text from each PDF, generates a prompt to compare their contents, and then uses the Google Generative AI model to highlight similarities and differences.

## Features

- **PDF Text Extraction**: Extracts text content from uploaded PDF files.
- **AI-Powered Comparison**: Uses Google's Generative AI model to identify and describe key similarities and differences between the two documents.
- **User-Friendly Interface**: Simple, styled UI with Bootstrap for ease of use.

## Prerequisites

- **Python** (3.8 or higher)
- **Google Cloud API Key**: To access Google Generative AI features.
- **Google Generative AI Python SDK**: Used to interact with Google's language model.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-document-comparison.git
cd pdf-document-comparison
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The dependencies include:
- Flask
- PyPDF2
- google-generativeai
- python-dotenv

### 3. Configure Environment Variables

Create a `.env` file in the root directory and add your Google API key:

```plaintext
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the Application

```bash
python app.py
```

The application will run on `http://127.0.0.1:5000`.

## Usage

1. Open the app in your browser at `http://127.0.0.1:5000`.
2. Upload two PDF files you want to compare.
3. Click **Compare Documents** to get AI-generated insights into the similarities and differences between the PDFs.

## Project Structure

```plaintext
├── app.py                # Main Flask application file
├── templates             # Directory for HTML templates (if added separately)
├── static                # Directory for static files like CSS (optional)
├── .env                  # Environment variables file (not in version control)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Key Files

- **app.py**: Contains the main Flask app with routes and functions to extract text from PDFs, compare them, and render the results.
- **requirements.txt**: Lists the required Python packages.

## Dependencies

- **Flask**: For building the web application.
- **PyPDF2**: To handle PDF file reading and text extraction.
- **google-generativeai**: To connect with the Google Generative AI model.
- **python-dotenv**: To manage environment variables securely.

## Additional Notes

- **Error Handling**: The app includes basic error handling for file uploads and API interactions.
- **API Limitations**: Ensure your Google API key has adequate quota to handle AI requests.

## Troubleshooting

- If the app does not load, check that the correct Python version is installed and that all dependencies are properly installed.
- For issues with AI responses, verify that your Google API key is correctly configured and has the necessary permissions.

---


---



## PDF Document Comparison Project using Flask, Google Generative AI, and PyPDF2.

---

### Project Structure
```plaintext
pdf-document-comparison/
├── app.py                # Main Flask application file
├── .env                  # Environment variables file (add API key here)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

### 1. `app.py`

This is the main application file:

```python
import os
from flask import Flask, request, render_template_string
from PyPDF2 import PdfReader
from google.generativeai import configure, GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Function to extract text from a PDF file
def extract_pdf_text(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Function to compare two texts and get AI-based insights
def compare_texts(text1, text2):
    model = GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Compare the following two documents for similarities and differences:

    Document 1:
    {text1}

    Document 2:
    {text2}

    Describe key similarities, differences, and potential conclusions.
    """
    response = model.generate_content(prompt)
    return response.text if response else "Comparison not available."

# Flask routes
@app.route("/", methods=["GET", "POST"])
def index():
    comparison_result = ""
    if request.method == "POST":
        # Get uploaded files
        pdf_file1 = request.files.get("pdf_file1")
        pdf_file2 = request.files.get("pdf_file2")
        
        # Check if both files are uploaded
        if pdf_file1 and pdf_file2:
            # Extract text from both PDFs
            text1 = extract_pdf_text(pdf_file1)
            text2 = extract_pdf_text(pdf_file2)

            # Generate comparison result using AI
            comparison_result = compare_texts(text1, text2)
        else:
            comparison_result = "Please upload both PDF files for comparison."

    # Render the HTML with enhanced styling
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Document Comparison</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f0f2f5; }
            .container { max-width: 800px; margin-top: 50px; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
            .btn-primary { background-color: #007bff; border-color: #007bff; }
            .text-block { white-space: pre-wrap; background-color: #f7f7f7; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; font-family: monospace; font-size: 0.9em; }
            h1 { font-size: 1.75em; color: #333; }
            h3 { font-size: 1.25em; color: #333; margin-top: 20px; }
            .instructions { font-size: 0.9em; color: #666; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">PDF Document Comparison</h1>
            <p class="instructions text-center">Upload two PDF files below, and the AI will highlight similarities and differences.</p>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="pdf_file1">Choose the first PDF file:</label>
                    <input type="file" class="form-control-file" id="pdf_file1" name="pdf_file1" accept=".pdf" required>
                </div>
                <div class="form-group mt-3">
                    <label for="pdf_file2">Choose the second PDF file:</label>
                    <input type="file" class="form-control-file" id="pdf_file2" name="pdf_file2" accept=".pdf" required>
                </div>
                <button type="submit" class="btn btn-primary mt-3">Compare Documents</button>
            </form>
            <hr class="mt-4">
            <h3>Comparison Results</h3>
            <div class="text-block">{{ comparison_result }}</div>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    '''.replace("{{ comparison_result }}", comparison_result)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
```

---




---
---
---
