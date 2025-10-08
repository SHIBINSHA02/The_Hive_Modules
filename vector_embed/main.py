# vector_embed_chat/main.py
import streamlit as st
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from collections import defaultdict

# --- Streamlit UI ---
st.set_page_config(page_title="Contract Multi-PDF Chat", layout="centered")

# --- Display Logo ---
logo_path = Path("logo.png")
if logo_path.exists():
    st.image(str(logo_path), width=150)

st.title("Contract Multi-PDF Chat Q&A")
st.write("Upload PDF contracts and chat with them. Answers are generated strictly from uploaded contract content, separated by source PDF.")

# --- Initialize session state ---
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
if "chunk_sources" not in st.session_state:
    st.session_state.chunk_sources = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Upload multiple PDFs ---
uploaded_files = st.file_uploader("Upload Contract PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.chunk_sources:
            pdf_reader = PdfReader(uploaded_file)
            contract_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    contract_text += text + "\n"

            if contract_text.strip():
                def split_text(text, chunk_size=500, overlap=50):
                    words = text.split()
                    chunks = []
                    for i in range(0, len(words), chunk_size - overlap):
                        chunk = " ".join(words[i:i+chunk_size])
                        chunks.append(chunk)
                    return chunks

                chunks = split_text(contract_text)
                st.session_state.pdf_chunks.extend(chunks)
                st.session_state.chunk_sources.extend([uploaded_file.name] * len(chunks))

    # Generate embeddings once
    if st.session_state.embeddings is None and st.session_state.pdf_chunks:
        st.info("Generating embeddings for uploaded contracts...")
        st.session_state.embeddings = embedding_model.encode(st.session_state.pdf_chunks, convert_to_numpy=True)
        st.success("Embeddings ready! You can start asking questions.")

# --- Load Mistral-7B model ---
if "generator" not in st.session_state and st.session_state.pdf_chunks:
    model_path = r"C:\Users\shibi\.cache\huggingface\hub\models--mistralai--Mistral-7B-Instruct-v0.2\snapshots\63a8b081895390a26e140280378bc85ec8bce07a"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype="auto")
    st.session_state.generator = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=300)

# --- Chat input ---
user_question = st.text_input("Ask a question about uploaded contracts:")

if user_question and st.session_state.pdf_chunks:
    query_vec = embedding_model.encode([user_question])
    sims = cosine_similarity(query_vec, st.session_state.embeddings)[0]

    # Group top chunks by source PDF
    source_to_chunks = defaultdict(list)
    top_indices = sims.argsort()[-9:][::-1]  # top 9 chunks overall
    for i in top_indices:
        source_to_chunks[st.session_state.chunk_sources[i]].append(st.session_state.pdf_chunks[i])

    # Generate answers per PDF
    pdf_answers = {}
    for source, chunks in source_to_chunks.items():
        context = "\n".join(chunks)
        prompt = f"""
You are a legal expert. Answer the following question strictly based on the contract content below. Do not use any outside knowledge.

Contract Content:
{context}

Question: {user_question}
Answer:
"""
        result = st.session_state.generator(prompt)[0]['generated_text']
        answer = result.split("Answer:")[-1].strip()
        pdf_answers[source] = answer

    # Store in chat history
    st.session_state.chat_history.append({"question": user_question, "answers": pdf_answers})

# --- Display chat history ---
for chat in st.session_state.chat_history:
    st.markdown(f"**Q:** {chat['question']}")
    for source, answer in chat["answers"].items():
        st.markdown(f"**Source PDF:** {source}")
        if answer.strip():
            st.markdown(f"**A:** {answer}")
        else:
            st.markdown("**A:** No relevant content found in this PDF.")
        st.markdown("---")
