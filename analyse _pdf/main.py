# analyse_pdf/main.py
import streamlit as st
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import re
from pathlib import Path

# --- Streamlit UI ---
st.set_page_config(page_title="Contract Compliance Analyzer", layout="centered")

# --- Display Logo ---
logo_path = Path("logo.png")  # replace with full path if not in the same folder
if logo_path.exists():
    st.image(str(logo_path), width=150)  # adjust width as needed

st.title("Contract Compliance Analyzer")
st.write("Upload a PDF contract and get a compliance summary with identified risks.")

uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])

if uploaded_file:
    # --- Extract PDF text ---
    pdf_reader = PdfReader(uploaded_file)
    contract_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            contract_text += text + "\n"

    if contract_text.strip() == "":
        st.error("Could not extract text from the PDF. Make sure it contains selectable text.")
    else:
        st.info("Contract text extracted successfully. Running compliance analysis...")

        # --- Load local Mistral 7B Instruct model ---
        model_path = r"C:\Users\shibi\.cache\huggingface\hub\models--mistralai--Mistral-7B-Instruct-v0.2\snapshots\63a8b081895390a26e140280378bc85ec8bce07a"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype="auto")

        # --- Setup a text-generation pipeline ---
        nlp = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512
        )

        # --- Prepare prompt for compliance analysis ---
        prompt = f"""
You are a legal compliance expert. Analyze the following contract content.
1. Give a clear summary of the contract in bullet points.
2. Identify potential risks or compliance issues.

Contract Content:
{contract_text}

Provide the answer in JSON format with keys 'summary' and 'risks'.
"""

        # --- Generate response ---
        response = nlp(prompt)[0]['generated_text']

        # --- Extract JSON from response ---
        try:
            # Extract JSON block using regex
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                st.error("Could not parse analysis result. Here's the raw output:")
                st.code(response)
                analysis = None

            if analysis:
                st.subheader("✅ Contract Summary")
                for idx, point in enumerate(analysis.get("summary", []), 1):
                    st.write(f"{idx}. {point}")

                st.subheader("⚠️ Potential Risks")
                for idx, risk in enumerate(analysis.get("risks", []), 1):
                    st.write(f"{idx}. {risk}")

        except json.JSONDecodeError:
            st.error("Failed to parse JSON. Here is the raw output:")
            st.code(response)
