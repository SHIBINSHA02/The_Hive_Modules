# generate_pdf/main.py
import streamlit as st
from datetime import datetime
from llm_handler import formalize_contract_text
from pdf import create_agreement_pdf

st.set_page_config(page_title="Construction Agreement Generator", page_icon="🏗️", layout="centered")
st.title("🏗️ Construction Agreement Generator")

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
st.subheader("🧑‍💼 Party Information")

st.session_state.contractor_name = st.text_input(
    "Contractor Name", value=st.session_state.contractor_name
)
st.session_state.contractor_address = st.text_area(
    "Contractor Address", value=st.session_state.contractor_address
)
st.session_state.client_name = st.text_input(
    "Client Name", value=st.session_state.client_name
)
st.session_state.client_address = st.text_area(
    "Client Address", value=st.session_state.client_address
)
agreement_date = st.date_input("Agreement Date", datetime.now())

st.divider()

# --- Contract Content Sections ---
st.subheader("📄 Agreement Details")

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

        # Store formatted results separately
        st.session_state.formatted_scope_of_work = formatted["scope_of_work"]
        st.session_state.formatted_project_timeline = formatted["project_timeline"]
        st.session_state.formatted_payment_details = formatted["payment_details"]
        st.session_state.pending_update = True  # Flag to apply on next render

        st.success("✅ Text formatted successfully! Updating fields...")
        st.rerun()  # Safe re-render so widgets show updated values

# --- Generate PDF Button ---
if st.button("📄 Generate Agreement PDF", use_container_width=True):
    with st.spinner("Generating agreement PDF..."):
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
            "Authorized Signatory", "Client Representative"
        )

        st.download_button(
            label="⬇️ Download Agreement PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state.contractor_name}_agreement.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.info("💡 Tip: You can edit the text fields before or after formatting, then regenerate the PDF anytime.")
