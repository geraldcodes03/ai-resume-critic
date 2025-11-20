import streamlit as st
import PyPDF2 
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # loads the environment variable from the dot env file

st.set_page_config(page_title = "AI Resume Critic", page_icon = "📃", layout = "centered") #initializes the page
st.title("AI Resume Critiquer") #here onwards is really all the different UI being rendered
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") #need to explicitly doing it now because we dont have langchain anymore
uploaded_file = st.file_uploader("Upload your PDF or TXT file here", type = ['pdf','txt'])
job_role = st.text_input('Enter the job role you are targetting(optional): ')
analyze = st.button("Analyze Resume") #changes to True when the button is pressed

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file): #LLM cannot read the file so we extract the text then we pass in the text into the LLM
    if uploaded_file.type == 'application/pdf':
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read())) #io.BytesIO creates a file-like object in RAM with the bytes of the pdf
    return uploaded_file.read().decode("utf-8")
    
if analyze and uploaded_file: 
    try: 
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop() #stops the program right there and then
        else: #create a prompt that contains the text from the pdf and pass it into the LLM and get the critic from the LLM

            prompt = f"""Please analyze this resume and provide constructive feedback. Focus on the following aspects:
            1. Content clarity
            2. Skills presentation
            3. Experience and descriptions
            4. Specific improvements for {job_role if job_role else 'general job applications'}

            Resume content: {file_content}

            Please provide your analysis in a clear and structred format with specific recommendations"""
            loading = True
            loading_placeholder = st.empty()
            loading_placeholder.markdown('### Analyzing Your Resume...')
            while (loading):
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model = "gpt-4o-mini",
                    messages = [
                        {"role": "system", #this gives the AI instructions before the convo starts
                        "content": "You are an expert resume reviewer"},
                        {"role":"user",
                        "content": prompt}
                    ],
                    temperature = 0.7,
                    max_tokens = 500
                )
                loading = False
            loading_placeholder.empty()
            st.markdown('### Analysis Results')
            st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f'Error occured: {str(e)}')