# generate_pdf/main.py
import streamlit as st
from datetime import datetime
from llm_handler import formalize_contract_text
from pdf import create_agreement_pdf

# Set page configuration with custom icon
st.set_page_config(page_title="Construction Agreement Generator", page_icon="🏗️", layout="centered")

# Apply custom CSS for #2c6df5 and white theme
st.markdown("""
    <style>
    /* Main button styling */
    div.stButton > button {
        background-color: #2c6df5;
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
    }
    div.stButton > button:hover {
        background-color: #1a5cd4;
        color: #ffffff;
    }
    /* Download button specific styling */
    div.stDownloadButton > button {
        background-color: #2c6df5;
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
    }
    div.stDownloadButton > button:hover {
        background-color: #1a5cd4;
        color: #ffffff;
    }
    /* Text input and textarea borders */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-color: #2c6df5;
    }
    /* Info and success message styling */
    .stAlert {
        background-color: #2c6df5;
        color: #ffffff;
    }
    /* Divider styling */
    hr {
        border-color: #2c6df5;
    }
    </style>
""", unsafe_allow_html=True)

# Display logo at the top
st.image("logo.png", width=200, caption="Company Logo")

st.title("Construction Agreement Generator")

# --- Initialize session state ---
default_keys = [
    "scope_of_work", "project_timeline", "payment_details",
    "contractor_name", "contractor_address", "client_name", "client_address"
]
for key in default_keys:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- Apply formatted content before widgets load (safe update step) ---
if "pending_update" in st.session_state and st.session_state.pending_update:
    st.session_state.scope_of_work = st.session_state.formatted_scope_of_work
    st.session_state.project_timeline = st.session_state.formatted_project_timeline
    st.session_state.payment_details = st.session_state.formatted_payment_details
    st.session_state.pending_update = False

# --- Contractor & Client Info ---
st.subheader("Party Information")

st.session_state.contractor_name = st.text_input("Contractor Name", value=st.session_state.contractor_name)
st.session_state.contractor_address = st.text_area("Contractor Address", value=st.session_state.contractor_address)
st.session_state.client_name = st.text_input("Client Name", value=st.session_state.client_name)
st.session_state.client_address = st.text_area("Client Address", value=st.session_state.client_address)
agreement_date = st.date_input("Agreement Date", datetime.now())

st.divider()

# --- Company Logo Upload ---
st.subheader("Company Branding")
uploaded_logo = st.file_uploader("Upload Company Logo (optional, PNG/JPG)", type=["png", "jpg", "jpeg"])
if uploaded_logo:
    st.image(uploaded_logo, width=200, caption="Company Logo Preview")

st.divider()

# --- Contract Content Sections ---
st.subheader("Agreement Details")

st.text_area("Scope of Work", key="scope_of_work", height=150)
st.text_area("Project Timeline", key="project_timeline", height=150)
st.text_area("Payment Details", key="payment_details", height=150)

st.divider()

# --- LLM Formatter Button ---
if st.button("✨ Format Text (LLM)", use_container_width=True):
    with st.spinner("Formalizing content using Mistral LLM..."):
        formatted = formalize_contract_text(
            st.session_state.scope_of_work,
            st.session_state.project_timeline,
            st.session_state.payment_details
        )

        st.session_state.formatted_scope_of_work = formatted["scope_of_work"]
        st.session_state.formatted_project_timeline = formatted["project_timeline"]
        st.session_state.formatted_payment_details = formatted["payment_details"]
        st.session_state.pending_update = True
        st.success("✅ Text formatted successfully! Updating fields...")
        st.rerun()

# --- Generate PDF Button ---
if st.button("📄 Generate Agreement PDF", use_container_width=True):
    with st.spinner("Generating agreement PDF..."):
        logo_bytes = uploaded_logo.read() if uploaded_logo else None

        pdf_bytes = create_agreement_pdf(
            st.session_state.contractor_name,
            st.session_state.contractor_address,
            st.session_state.client_name,
            st.session_state.client_address,
            agreement_date,
            st.session_state.scope_of_work,
            st.session_state.project_timeline,
            st.session_state.payment_details,
            "Authorized Signatory", "Manager",
            "Authorized Signatory", "Client Representative",
            logo_bytes=logo_bytes
        )

        st.download_button(
            label="⬇️ Download Agreement PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state.contractor_name}_agreement.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.info("💡 Tip: You can upload a logo, format text using LLM, and regenerate the PDF anytime.")