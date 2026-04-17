# 🧬 PHARMA-GUARD AI ELITE

> **Advanced Autonomous Multi-Agent Molecular Intelligence**

Pharma-Guard is a state-of-the-art pharmaceutical analysis system that leverages a decentralized agent architecture to provide zero-tolerance safety verification for medications. Using Gemini 2.0 and Llama-3, it bridges the gap between optical character recognition and official clinical documentation (RAG).

## 🚀 Key Protocols

- **Vision-Scanner (LLaVA v1.6)**: Decodes complex pharmaceutical packaging and extracts molecular data.
- **RAG-Specialist (ChromaDB)**: Real-time semantic search across official TITCK/FDA PDF prospectuses.
- **Safety-Auditor (Llama-3-70B)**: Instant clinical risk simulation and contraindication analysis.
- **Elite UI**: A high-contrast, glassmorphism-based command center for medical intelligence.

## 🛠 Deployment Sequence

1. **Environmental Setup**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Neural Interface Configuration**:
   Create a `.env` file or use the Elite UI Sidebar to input:
   ```env
   GROQ_API_KEY=your_groq_key
   ```
   *Note: Ensure the `fonts/` directory containing Arial TTF files is present for PDF generation support.*

3. **Knowledge Base Induction**:
   Place official drug PDF prospectuses in `data/corpus/`.

4. **Initiate Core**:
   ```bash
   streamlit run app.py
   ```

## ⚠️ Tactical Disclaimer
This system is an AI-driven prototype designed for research and educational purposes. Always cross-reference with certified medical professionals.

---
*Developed by the PharmaGuard Core Team*
