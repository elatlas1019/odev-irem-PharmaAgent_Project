import streamlit as st
import os
import json
from PIL import Image
from dotenv import load_dotenv
from utils import get_vision_analysis, generate_pdf_report
from agents import PharmaGuardOrchestrator

# Configuration
load_dotenv()
st.set_page_config(
    page_title="Pharma-Guard AI Groq-Elite",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    
    :root {
        --primary: #f43f5e; /* Rose/Coral */
        --secondary: #6366f1; /* Indigo */
        --accent: #10b981; /* Emerald */
        --bg-dark: #0f172a;
    }

    .main {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        color: #f8fafc;
        font-family: 'Rajdhani', sans-serif;
    }

    .stApp {
        background: transparent;
    }

    /* Glassmorphism Containers */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-16idsys {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px !important;
        padding: 2.5rem !important;
    }

    /* Vibrant Titles */
    h1 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(to right, #f43f5e, #fb923c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        text-align: center;
        letter-spacing: 4px;
        margin-bottom: 0.5rem !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #f43f5e, #fb923c) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 20px -10px rgba(244, 63, 94, 0.5) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 30px -10px rgba(244, 63, 94, 0.6) !important;
    }

    .metric-card {
        background: rgba(255,255,255,0.02);
        border-left: 6px solid var(--primary);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Application Header
st.markdown("<h1>💊 PHARMA-GUARD <span style='color:#f8fafc'>GROQ</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.3rem; color:#94a3b8; margin-top:-1rem;'>🚀 Ultra-Fast Groq-Powered Multi-Agent Intelligence</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#f43f5e;'>🧬 Core Control</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022245.png", width=120)
    
    groq_api = st.text_input("Groq Cloud API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    
    if groq_api:
        os.environ["GROQ_API_KEY"] = groq_api
        st.success("✅ Neural Links: GROQ ACTIVE")
    else:
        st.warning("⚠️ GROQ API KEY REQUIRED")

    st.divider()
    st.markdown("""
        ### 🤖 Groq Cluster Status
        - **Vision**: Llama-4-Scout
        - **Logic**: Llama-3.3-70B
        - **Safety**: Llama-3.3-70B
        - **Embeddings**: Local (Free)
    """)

# Layout
col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.markdown("### 📸 Visual Scan Input")
    uploaded_file = st.file_uploader("Upload drug packaging scan...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True, caption="Target Scan Loaded")
        
        if st.button("⚡ INITIATE GROQ SCAN"):
            if not os.environ.get("GROQ_API_KEY"):
                st.error("Error: Missing Groq API Credentials")
            else:
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, "groq_scan.png")
                img.save(temp_path)
                
                with st.status("🛸 Orchestrating Groq Cluster...", expanded=True) as status:
                    st.write("📡 [Vision-Scanner] Groq Vision decoding...")
                    vision_result = get_vision_analysis(temp_path)
                    
                    if "error" in vision_result.lower():
                        st.error(f"❌ SCAN FAILURE: {vision_result}")
                        status.update(label="Groq Cluster Failure", state="error")
                    else:
                        st.write("📚 [RAG-Specialist] Scanning local knowledge...")
                        orchestrator = PharmaGuardOrchestrator()
                        
                        st.write("🛡️ [Safety-Auditor] Verifying clinical risks...")
                        report_data = orchestrator.run_analysis(vision_result)
                        
                        st.write("📊 [Report-Synthesizer] Sentezleniyor...")
                        status.update(label="Groq Analysis Protocol Complete", state="complete")
                        st.session_state['active_report'] = report_data

with col_right:
    st.markdown("### 📋 Intelligence Report")
    if 'active_report' in st.session_state:
        report = st.session_state['active_report']
        
        if "error" in report:
            st.error(report["error"])
        else:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='margin:0; color:#f43f5e;'>{report['summary']}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            t1, t2, t3 = st.tabs(["🧬 Synthesis", "⚠️ Bio-Safety", "📋 Sources"])
            
            with t1:
                st.markdown(report['full_text'])
            with t2:
                st.warning(report['warnings'])
            with t3:
                st.info(report['sources'])
                
            if st.button("💾 DOWNLOAD PDF REPORT"):
                pdf_path = "PharmaGuard_Report.pdf"
                generate_pdf_report(report, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Save Secure PDF",
                        data=f,
                        file_name=f"Groq_Report_{report['summary'].replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
    else:
        st.markdown("<div style='height:400px; border:2px dashed #475569; border-radius:24px; display:flex; align-items:center; justify-content:center; color:#64748b;'>Waiting for Groq sensor input...</div>", unsafe_allow_html=True)

st.divider()
st.markdown("<p style='text-align:center; color:#475569; font-size:0.8rem;'>DISCLAIMER: This system is an AI prototype. Consult biological medical professionals for actual prescriptions.</p>", unsafe_allow_html=True)
