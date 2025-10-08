# generate_pdf/pdf.py
from fpdf import FPDF
from datetime import datetime
import os
import tempfile

class AgreementPDF(FPDF):
    def __init__(self, contractor_name, client_name):
        super().__init__()
        self.contractor_name = contractor_name
        self.client_name = client_name
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=50)

        # Add Unicode-safe font
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
        if os.path.exists(font_path):
            self.add_font("DejaVu", "", font_path, uni=True)
            self.set_font("DejaVu", "", 12)
        else:
            self.set_font("Arial", "", 12)

    # ---------- Footer ----------
    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", size=10)
        self.cell(90, 10, f"{self.contractor_name}", ln=False, align='L')
        self.cell(90, 10, f"{self.client_name}", ln=True, align='R')
        self.cell(90, 5, "__________________________", ln=False, align='L')
        self.cell(90, 5, "__________________________", ln=True, align='R')
        self.cell(90, 5, "Signature", ln=False, align='L')
        self.cell(90, 5, "Signature", ln=True, align='R')
        self.ln(3)
        self.set_font("Arial", 'I', 9)
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align='C')


# ---------- Utility Function ----------
def sanitize_text(text: str) -> str:
    replacements = {
        "—": "-", "–": "-", "“": '"', "”": '"',
        "’": "'", "‘": "'", "₹": "INR", "•": "-", "‣": "-", "‒": "-"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


# ---------- Main PDF Generator ----------
def create_agreement_pdf(
    contractor_name, contractor_address,
    client_name, client_address,
    agreement_date, scope_of_work,
    project_timeline, payment_details,
    contractor_signer_name, contractor_signer_title,
    client_signer_name, client_signer_title,
    logo_bytes=None  # optional
):
    pdf = AgreementPDF(contractor_name, client_name)
    pdf.add_page()

    # ---------- Header with Left-Aligned Logo ----------
    if logo_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(logo_bytes)
            tmp.flush()
            # Draw logo in top-left corner (x=10, y=10)
            pdf.image(tmp.name, x=10, y=10, w=30)
        pdf.set_y(10)  # ensure proper spacing
        pdf.ln(25)     # space below the logo
    else:
        pdf.ln(15)

    # ---------- Title and Date ----------
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", "B", 16)
    pdf.cell(0, 10, txt="Construction Agreement", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", "", 12)
    pdf.cell(0, 10, txt=f"Date: {agreement_date.strftime('%B %d, %Y')}", ln=True, align='R')
    pdf.ln(10)

    # ---------- Parties ----------
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", 'B', 12)
    pdf.cell(0, 10, txt="Parties:", ln=True)
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", "", 12)
    pdf.multi_cell(0, 6, sanitize_text(
        f'This Construction Agreement ("Agreement") is entered into on {agreement_date.strftime("%B %d, %Y")}, '
        f'between {contractor_name} (Contractor), located at {contractor_address}, and '
        f'{client_name} (Client), located at {client_address}.'
    ))
    pdf.ln(10)

    # ---------- Contract Sections ----------
    sections = [
        ("1. Scope of Work:", scope_of_work),
        ("2. Project Timeline:", project_timeline),
        ("3. Payment Details:", payment_details),
    ]

    for title, content in sections:
        pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", 'B', 12)
        pdf.cell(0, 10, txt=title, ln=True)
        pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", "", 12)
        pdf.multi_cell(0, 6, sanitize_text(content))
        pdf.ln(5)

    # ---------- Signatories ----------
    pdf.ln(10)
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", 'B', 12)
    pdf.cell(0, 10, txt="Authorized Signatories:", ln=True)
    pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", "", 12)
    pdf.multi_cell(0, 6, sanitize_text(
        f"{contractor_signer_name}, {contractor_signer_title} — for {contractor_name}\n"
        f"{client_signer_name}, {client_signer_title} — for {client_name}"
    ))

    # ---------- Return PDF Bytes ----------
    return bytes(pdf.output(dest='S'))
