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
Here's the complete code for your PDF Document Comparison project using Flask, Google Generative AI, and PyPDF2.

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

### 2. `.env`

This file contains your environment variables, including your Google API key:

```plaintext
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. `requirements.txt`

List of dependencies required for the project:

```plaintext
Flask==2.0.1
PyPDF2==3.0.0
google-generativeai==0.1.0
python-dotenv==0.19.0
```




---
---
---
