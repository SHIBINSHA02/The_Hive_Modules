# generate_pdf/pdf.py
from fpdf import FPDF
from datetime import datetime

class AgreementPDF(FPDF):
    def __init__(self, contractor_name, client_name):
        super().__init__()
        self.contractor_name = contractor_name
        self.client_name = client_name
        self.alias_nb_pages()  # enables {nb} placeholder

    def footer(self):
        # Set position 40 mm from bottom
        self.set_y(-40)
        self.set_font("Arial", size=10)

        # Signature Lines
        self.cell(90, 10, f"{self.contractor_name}", ln=False, align='L')
        self.cell(90, 10, f"{self.client_name}", ln=True, align='R')

        self.cell(90, 5, "__________________________", ln=False, align='L')
        self.cell(90, 5, "__________________________", ln=True, align='R')

        self.cell(90, 5, "Signature", ln=False, align='L')
        self.cell(90, 5, "Signature", ln=True, align='R')

        # Move down for spacing
        self.ln(5)
        # Page number centered at bottom
        self.set_font("Arial", 'I', 9)
        page_text = f"Page {self.page_no()} of {{nb}}"
        self.cell(0, 10, page_text, align='C')

def create_agreement_pdf(contractor_name, contractor_address, client_name, client_address, agreement_date, scope_of_work, project_timeline, payment_details, contractor_signer_name, contractor_signer_title, client_signer_name, client_signer_title):
    pdf = AgreementPDF(contractor_name, client_name)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # --- Title ---
    pdf.cell(200, 10, txt="Construction Agreement", ln=True, align='C')
    pdf.ln(10)

    # --- Agreement Date ---
    pdf.cell(200, 10, txt=f"Date: {agreement_date.strftime('%B %d, %Y')}", ln=True)
    pdf.ln(5)

    # --- Parties ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Parties:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, txt=(
        f'This Construction Agreement (the "Agreement") is entered into as of {agreement_date.strftime("%B %d, %Y")}, '
        f'by and between:\n\n'
        f'{contractor_name}, a company registered under the laws of India, having its registered office at {contractor_address} '
        f'(hereinafter referred to as the "Contractor"),\n\nand\n\n'
        f'{client_name}, a company registered under the laws of India, having its registered office at {client_address} '
        f'(hereinafter referred to as the "Client").'
    ))
    pdf.ln(10)

    # --- Background ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Background:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, txt=(
        "The Client desires to engage the Contractor to perform certain construction services, including the "
        "construction of a residential apartment complex, and the Contractor is willing to provide such services, "
        "subject to the terms and conditions set forth in this Agreement."
    ))
    pdf.ln(10)

    # --- Scope of Work ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="1. Scope of Work:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, txt=scope_of_work)
    pdf.ln(5)

    # --- Project Timeline ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="2. Project Timeline:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, txt=project_timeline)
    pdf.ln(5)

    # --- Payment Details ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="3. Payment:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, txt=payment_details)
    pdf.ln(10)

    # --- Final Signature Block on Last Page (optional redundancy) ---
    pdf.ln(20)
    pdf.cell(95, 10, txt=contractor_name, ln=False)
    pdf.cell(95, 10, txt=client_name, ln=True, align='R')
    pdf.cell(95, 10, txt="By: ____________________", ln=False)
    pdf.cell(95, 10, txt="By: ____________________", ln=True, align='R')
    pdf.ln(5)
    pdf.cell(95, 5, txt=f"Name: {contractor_signer_name}", ln=False)
    pdf.cell(95, 5, txt=f"Name: {client_signer_name}", ln=True, align='R')
    pdf.cell(95, 5, txt=f"Title: {contractor_signer_title}", ln=False)
    pdf.cell(95, 5, txt=f"Title: {client_signer_title}", ln=True, align='R')

    # Return as bytes
    return bytes(pdf.output(dest='S'))
