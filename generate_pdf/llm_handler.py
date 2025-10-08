# generate_pdf/llm_handler.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Local snapshot path for Mistral ---
model_path = r"C:\Users\shibi\.cache\huggingface\hub\models--mistralai--Mistral-7B-Instruct-v0.2\snapshots\63a8b081895390a26e140280378bc85ec8bce07a"

if not os.path.isdir(model_path):
    raise FileNotFoundError(
        f"❌ Model directory not found at: {model_path}\n"
        "Please ensure you provided the correct snapshot path."
    )

print(f"✅ Loading model from local snapshot: {model_path}")

# --- Load Tokenizer and Model ---
# Tip: Mistral base model is NOT tuned for instructions.
# For better results, use Mistral-7B-Instruct-v0.1 if available locally.
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path, legacy=False)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    print("✅ Model and tokenizer loaded successfully.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load local model: {e}")

# --- Main Function ---
def formalize_contract_text(scope_of_work, project_timeline, payment_details):
    """
    Uses a local Mistral-7B model to formalize construction agreement text
    into legally suitable contract language.
    """

    prompt = f"""
    <s>[INST] You are an expert legal contract drafter.
    Rewrite the following construction contract sections into
    a formal, precise, and professional legal tone
    suitable for an Indian construction agreement.

    Clearly separate the rewritten text into:
    --- Scope of Work ---
    --- Project Timeline ---
    --- Payment Details ---

    Do not include any additional commentary or explanations.

    --- Scope of Work ---
    {scope_of_work}

    --- Project Timeline ---
    {project_timeline}

    --- Payment Details ---
    {payment_details} [/INST]
    """

    try:
        # --- Tokenize prompt ---
        inputs = tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # --- Generate completion ---
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )

        formatted_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # --- Remove the prompt from model output ---
        instruction_end_tag = "[/INST]"
        if instruction_end_tag in formatted_text:
            formatted_text = formatted_text.split(instruction_end_tag, 1)[1].strip()

    except Exception as e:
        print(f"[LLM Error] Local model generation failed: {e}")
        return {
            "scope_of_work": scope_of_work,
            "project_timeline": project_timeline,
            "payment_details": payment_details
        }

    # --- Parse model response into sections ---
    sections = {
        "scope_of_work": "",
        "project_timeline": "",
        "payment_details": ""
    }

    try:
        if "--- Scope of Work ---" in formatted_text:
            parts = formatted_text.split("--- Scope of Work ---")[1]
            if "--- Project Timeline ---" in parts:
                scope_part, rest = parts.split("--- Project Timeline ---", 1)
                sections["scope_of_work"] = scope_part.strip()
                if "--- Payment Details ---" in rest:
                    timeline_part, payment_part = rest.split("--- Payment Details ---", 1)
                    sections["project_timeline"] = timeline_part.strip()
                    sections["payment_details"] = payment_part.strip()
                else:
                    sections["project_timeline"] = rest.strip()
            else:
                sections["scope_of_work"] = parts.strip()
        else:
            sections["scope_of_work"] = formatted_text

    except Exception as parse_err:
        print(f"[Parse Error] Failed to parse LLM response: {parse_err}")
        sections["scope_of_work"] = formatted_text

    return sections


# --- Example Run ---
if __name__ == '__main__':
    scope = "Build a two-story house with 3 bedrooms and 2 bathrooms. Use good quality bricks and cement. Painting should be done with weatherproof paint."
    timeline = "Start on Nov 1st, 2023 and finish by May 1st, 2024. Foundation should be done in one month. First floor in 2 months. Second floor in 2 months. Finishing in 1 month."
    payment = "Total cost is 50 lakhs. 10 lakhs advance. 15 lakhs after foundation. 15 lakhs after first floor. 10 lakhs on completion."

    formatted = formalize_contract_text(scope, timeline, payment)

    print("\n--- Formalized Scope of Work ---")
    print(formatted["scope_of_work"])
    print("\n--- Formalized Project Timeline ---")
    print(formatted["project_timeline"])
    print("\n--- Formalized Payment Details ---")
    print(formatted["payment_details"])
