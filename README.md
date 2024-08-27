## Gemini_MultiModel_App

## URL :
Render : [https://gemini-multimodel-app.onrender.com/ ](https://gemini-multimodel-app.onrender.com)

streamlitCloud : [https://satyam-multimodel-gemini-ai-app.streamlit.app/](https://satyam-multimodel-gemini-ai-app.streamlit.app/)

![image](https://github.com/user-attachments/assets/14bc75d8-9032-4a56-be40-988a21ae05ee)



# All steps to make this project:

# 1. Virtual Environment Setup

**Step 1: Create a virtual environment**

python -m venv venv

**Step 2: Activate the virtual environment**

Windows:

.\venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

# 2. Dependencies Install Karo

**Step 3: Create a requirements.txt file with all the dependencies listed**

echo "streamlit
google-generativeai
python-dotenv
langchain
PyPDF2
chromadb
faiss-cpu
langchain_google_genai
pillow
streamlit-option-menu
langchain_community
gtts
SpeechRecognition
playsound==1.2.2" > requirements.txt

**Step 4: Install the dependencies**

pip install -r requirements.txt


# 3. Environment Variables Setup

**Step 5: Create a .env file and add your environment variables (e.g., API keys)**

GOOGLE_API_KEY=your_google_api_key_here > .env

# 4. Main Application Script Setup
---

# 5. Run the Streamlit Application

**Run the Streamlit app locally**

streamlit run app.py

# 6. Deployment (Optional)

Deploy the app to Streamlit Cloud, Heroku, or another platform
