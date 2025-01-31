import streamlit as st
import pypdf
import json
import requests

# Function to read PDF and extract text
def read_pdf(file):
	  pages = []
	  pdf = pypdf.PdfReader(file)
	  for p in range(len(pdf.pages)):
		  page = pdf.pages[p]
		  text = page.extract_text()
		  pages += [text]
	  return pages

# Set layout
st.set_page_config(
    page_title="Earning Release Analyst",
    layout="wide",
    page_icon="logo2.png")

# Set Title and Message
st.markdown(
        """
	# Unleash the power of ER app 🚀
 	This app uses Mistral AI to generate summaries of earnings releases (ER) from companies, providing: 
	* Sentiment Analysis
 	* Key Words
	* Executive Summary
	Please upload your Hugging Face Key and the PDF to get the best ER analysis !!
""" 
    )

# Set Sidebar
st.sidebar.markdown("Earning Releases (ER) App")
st.sidebar.image("logo2.png", width=150)
with st.sidebar:
    hf_api_key = st.text_input("Enter your Hugging Face API key", type="password")

# Upload the file
uploaded_file = st.file_uploader("Upload a file", type=("txt", "md", "pdf"))

# Parse the file
if uploaded_file and hf_api_key:

    if uploaded_file.type == "application/pdf":
        article = read_pdf(uploaded_file)
    else:
        article = uploaded_file.read().decode()

    # Prompt for LLM
    prompt = f"""
    Act as a company financial analyst to analyze the earnings releases of companies.
    
    Output should include:

    **Overall sentiment**: <positive, negative or neutral; keeping in mind that companies will often appear to be extremely optimistic about their company performance>
    **Key words**: <find those key words which are the most important drivers of growth and performance for the company, include only 10 words max>
    **Executive summary**: <executive summary of past performance and about future earning growth, 10 lines max>

    Keep all information factual, short and concise and only include information extracted from the earning release document delimited below by triple backticks.

    Earning release document:
    ```{article}```
    """

    # Define query function
    def query(payload, model_api_url):
        headers = {"Authorization": f"Bearer {hf_api_key}"}
        response = requests.post(model_api_url, headers=headers, json=payload)
        return response.json()

    # LLM model parameters
    mistral_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    mistral_params = {
                  "wait_for_model": True,
                  "do_sample": False,
                  "return_full_text": False,
                  "max_new_tokens": 5000,
                  "repetition_penalty": 1.5,
                  "temperature": 0.001
                }

    # LLM model request
    output = query(payload={"inputs": prompt, "parameters": mistral_params}, model_api_url=mistral_api_url)

    # Display result
    st.write("### Answer")
    st.write(output[0]['generated_text'])
