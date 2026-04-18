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
    page_title="odev-irem-PharmaAgent_Project",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium White & Medical Theme CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    :root {
        --primary: #0ea5e9; /* Medical Blue */
        --secondary: #10b981; /* Emerald Green */
        --accent: #f59e0b; /* Amber */
        --bg-light: #f8fafc; /* Very light slate for background */
        --text-main: #0f172a;
    }

    .main {
        background-color: var(--bg-light);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: transparent;
    }

    /* Clean White Containers */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-16idsys {
        background: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Vibrant Medical Titles */
    h1 {
        font-family: 'Inter', sans-serif;
        color: var(--primary) !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .developer-text {
        text-align: center;
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 600;
        margin-top: -1rem;
        margin-bottom: 2rem;
    }

    /* Buttons */
    .stButton>button {
        background: var(--secondary) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.4) !important;
        background: #059669 !important;
    }

    .metric-card {
        background: #ffffff;
        border-left: 6px solid var(--primary);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: var(--text-main);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Application Header
st.markdown("<h1>🏥 odev-irem-PharmaAgent_Project</h1>", unsafe_allow_html=True)
st.markdown("<p class='developer-text'>Geliştirici: ⚕️ İREM BURCU ORHAN</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#0ea5e9;'>🩺 Kontrol Paneli</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'><span style='font-size: 4rem;'>💊</span></div>", unsafe_allow_html=True)
    
    groq_api = st.text_input("Groq Cloud API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    
    if groq_api:
        os.environ["GROQ_API_KEY"] = groq_api
        st.success("✅ Sistem Aktif: API Bağlantısı Başarılı")
    else:
        st.warning("⚠️ Lütfen GROQ API Anahtarını Giriniz")

    st.divider()
    st.markdown("""
        ### 🤖 Sistem Durumu
        - **Görüntü İşleme**: Aktif 📸
        - **Tıbbi Analiz**: Aktif 🔬
        - **Güvenlik Denetimi**: Aktif 🛡️
        - **Veritabanı**: Yerel (Ücretsiz) 🗄️
    """)

# Layout
col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.markdown("### 📸 İlaç Kutusu Taraması")
    uploaded_file = st.file_uploader("İlaç kutusunun fotoğrafını yükleyin...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True, caption="Yüklenen İlaç Görseli")
        
        if st.button("⚡ ANALİZİ BAŞLAT"):
            if not os.environ.get("GROQ_API_KEY"):
                st.error("Hata: Groq API Anahtarı eksik. Lütfen sol menüden ekleyin.")
            else:
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, "groq_scan.png")
                img.save(temp_path)
                
                with st.status("🛸 Analiz Yürütülüyor...", expanded=True) as status:
                    st.write("📡 [Görüntü-Tarayıcı] Görsel analiz ediliyor...")
                    vision_result = get_vision_analysis(temp_path)
                    
                    if "error" in vision_result.lower():
                        st.error(f"❌ TARAMA HATASI: Lütfen daha net bir fotoğraf yükleyin. Detay: {vision_result}")
                        status.update(label="Tarama Başarısız", state="error")
                    else:
                        st.write("📚 [Veri-Uzmanı] Tıbbi kaynaklar taranıyor...")
                        orchestrator = PharmaGuardOrchestrator()
                        
                        st.write("🛡️ [Güvenlik-Denetçisi] Klinik riskler doğrulanıyor...")
                        report_data = orchestrator.run_analysis(vision_result)
                        
                        st.write("📊 [Rapor-Sentezleyici] Nihai rapor oluşturuluyor...")
                        status.update(label="Analiz Protokolü Tamamlandı", state="complete")
                        st.session_state['active_report'] = report_data

with col_right:
    st.markdown("### 📋 Tıbbi Zeka Raporu")
    if 'active_report' in st.session_state:
        report = st.session_state['active_report']
        
        if "error" in report:
            st.error(report["error"])
        else:
            st.markdown(f"""
                <div class='metric-card'>
                    <h2 style='margin:0; color:#0ea5e9;'>⚕️ {report.get('summary', 'İlaç Özeti')}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            t1, t2, t3 = st.tabs(["🧬 Sentez", "⚠️ Biyo-Güvenlik", "📋 Kaynaklar"])
            
            with t1:
                st.markdown(report.get('full_text', 'Veri bulunamadı.'))
            with t2:
                st.warning(report.get('warnings', 'Uyarı bulunamadı.'))
            with t3:
                st.info(report.get('sources', 'Kaynak belirtilmedi.'))
                
            if st.button("💾 PDF RAPORUNU İNDİR"):
                pdf_path = "PharmaAgent_Report.pdf"
                try:
                    generate_pdf_report(report, pdf_path)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Güvenli PDF'i Kaydet",
                            data=f,
                            file_name=f"Rapor_{report.get('summary', 'Ilac').replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"PDF oluşturma hatası: {str(e)}")
    else:
        st.markdown("<div style='height:400px; border:2px dashed #cbd5e1; border-radius:24px; display:flex; align-items:center; justify-content:center; color:#94a3b8;'>Sistem hazır, görsel yüklemeniz bekleniyor... 💉</div>", unsafe_allow_html=True)

st.divider()
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.8rem;'>⚠️ YASAL UYARI: Bu sistem bir yapay zeka prototipidir. Kesin teşhis ve tedavi için lütfen bir tıp uzmanına veya eczacıya danışın.</p>", unsafe_allow_html=True)
