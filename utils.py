# Pharma-Guard AI Utility Module
import os
import json
import base64
from PIL import Image
from fpdf import FPDF
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_vision_analysis(image_path):
    """
    Uses Groq Llama 3.2 Vision for drug box analysis.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return json.dumps({"error": "Missing GROQ_API_KEY"})

    client = Groq(api_key=api_key)
    base64_image = encode_image(image_path)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this drug packaging. Extract information and return ONLY a JSON object: {\"commercial_name\": \"...\", \"active_ingredient\": \"...\", \"dosage\": \"...\", \"form\": \"...\", \"barcode\": \"...\"}. If unreadable, return {\"error\": \"unreadable\"}."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-90b-vision-preview",
        )
        response_text = chat_completion.choices[0].message.content
        # Clean potential markdown
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        return clean_json
    except Exception as e:
        return json.dumps({"error": f"Groq Vision Error: {str(e)}"})

class ModernPharmaPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register Unicode-compatible fonts (ensure fonts/ directory is included in deployment)
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        
        # Style mapping: (suffix, style_flag)
        styles = [
            ("arial.ttf", ""),
            ("arialbd.ttf", "B"),
            ("ariali.ttf", "I"),
            ("arialbi.ttf", "BI")
        ]
        
        for font_file, style in styles:
            path = os.path.join(font_dir, font_file)
            if os.path.exists(path):
                try:
                    self.add_font('ArialCustom', style, path)
                except Exception:
                    pass

    def header(self):
        self.set_fill_color(14, 165, 233) # Medical Blue
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        
        # Determine font and style
        font_name = 'ArialCustom' if 'ArialCustom' in self.fonts else 'helvetica'
        self.set_font(font_name, 'B', 20)
        self.cell(0, 20, 'odev-irem-PharmaAgent_Project', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        font_name = 'ArialCustom' if 'ArialCustom' in self.fonts else 'helvetica'
        # Check if Italic is available for ArialCustom
        style = 'I' if 'ArialCustom' in self.fonts and any(f.style == 'I' for f in self.fonts['ArialCustom'].values() if hasattr(f, 'style')) else ''
        # Simpler check for fpdf2
        try:
            self.set_font(font_name, 'I', 8)
        except:
            self.set_font(font_name, '', 8)
            
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'PharmaAgent AI Raporu - Gelistirici: IREM BURCU ORHAN | Sayfa {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(data, output_path):
    pdf = ModernPharmaPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_text_color(0, 0, 0)
    
    sections = [
        ("KIMLIK OZETI", data.get("summary", "N/A")),
        ("KULLANIM AMACI", data.get("indications", "N/A")),
        ("BIYO-GUVENLIK UYARILARI", data.get("warnings", "N/A")),
        ("FARMAKOLOJIK DETAYLAR", data.get("details", "N/A")),
        ("KAYNAKCA", data.get("sources", "N/A"))
    ]

    font_name = 'ArialCustom' if 'ArialCustom' in pdf.fonts else 'helvetica'

    def _safe_text(text):
        if font_name == 'helvetica':
            replacements = {'ı':'i', 'İ':'I', 'ğ':'g', 'Ğ':'G', 'ü':'u', 'Ü':'U', 'ş':'s', 'Ş':'S', 'ö':'o', 'Ö':'O', 'ç':'c', 'Ç':'C'}
            for tr, en in replacements.items():
                text = text.replace(tr, en)
        return text

    for title, content in sections:
        pdf.set_font(font_name, 'B', 14)
        pdf.set_text_color(14, 165, 233) # Medical Blue
        pdf.cell(0, 10, _safe_text(title), ln=True)
        pdf.ln(2)
        
        pdf.set_font(font_name, '', 11)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(0, 6, _safe_text(str(content)))
        pdf.ln(8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(output_path)
    return output_path
