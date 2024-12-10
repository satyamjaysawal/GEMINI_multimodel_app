

```

# Install necessary libraries
# !pip install google-generativeai

import google.generativeai as genai

# Set your API key
GOOGLE_API_KEY = "AIzaSyCq6fkWlTcWfWYaPAfer1nFhOiQuof1c4M" 

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini 1.5 Flash model
model = genai.GenerativeModel('gemini-1.5-flash')  # Load the model

# Query the model and generate a response
user_query = "Who is the Prime Minister of India?"
response = model.generate_content([user_query])  # Input as a list

# Print the response
print("\nGemini 1.5 Flash Model's Response:")
print(response.text)




```
