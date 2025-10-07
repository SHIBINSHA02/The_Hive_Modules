# generate_pdf/main.py
import streamlit as st
from datetime import datetime
from pdf import create_agreement_pdf  # 👈 import your generator function

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Construction Agreement Generator", layout="centered")

st.title("🏗️ Construction Agreement PDF Generator")
st.write("Fill in the details below to automatically generate a legally formatted Construction Agreement PDF.")

# --- Input Form ---
with st.form("agreement_form"):
    agreement_date = st.date_input("Agreement Date", datetime.now())

    st.subheader("Contractor Details")
    contractor_name = st.text_input("Contractor Name", "ABC Builders Pvt. Ltd.")
    contractor_address = st.text_area("Contractor Address", "123 Main Street, Mumbai, Maharashtra")
    contractor_signer_name = st.text_input("Contractor Signatory Name", "John Doe")
    contractor_signer_title = st.text_input("Contractor Signatory Title", "Managing Director")

    st.subheader("Client Details")
    client_name = st.text_input("Client Name", "XYZ Developers Pvt. Ltd.")
    client_address = st.text_area("Client Address", "456 Oak Avenue, Bangalore, Karnataka")
    client_signer_name = st.text_input("Client Signatory Name", "Jane Smith")
    client_signer_title = st.text_input("Client Signatory Title", "CEO")

    st.subheader("Project Details")
    scope_of_work = st.text_area("Scope of Work (Exhibit A)", 
        "Provide construction services, including site preparation, building construction, plumbing, electrical work, and finishing.")
    project_timeline = st.text_area("Project Timeline (Exhibit B)", 
        "The project shall commence on [Start Date] and is expected to be completed by [End Date]. Milestones will be detailed separately.")
    payment_details = st.text_area("Payment Details (Exhibit C)", 
        "The Client shall pay the Contractor INR 10,00,000 in installments as per the agreed payment schedule.")

    submitted = st.form_submit_button("Generate Agreement PDF")

# --- Generate PDF ---
if submitted:
    with st.spinner("Generating PDF... Please wait."):
        pdf_bytes = create_agreement_pdf(
            contractor_name, contractor_address,
            client_name, client_address,
            agreement_date,
            scope_of_work, project_timeline, payment_details,
            contractor_signer_name, contractor_signer_title,
            client_signer_name, client_signer_title
        )

        st.success("✅ PDF generated successfully!")

        # Download button
        st.download_button(
            label="📄 Download Agreement PDF",
            data=pdf_bytes,
            file_name=f"Construction_Agreement_{agreement_date.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )
