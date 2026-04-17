try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import json
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class PharmaGuardOrchestrator:
    def __init__(self, corpus_path="data/corpus/"):
        self.corpus_path = corpus_path
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing. Please configure it in the sidebar.")
            
        # Using a free, local embedding model (no API key needed)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self._initialize_rag()
        self.groq_client = Groq(api_key=self.groq_api_key)

    def _initialize_rag(self):
        if not os.path.exists(self.corpus_path):
            os.makedirs(self.corpus_path)
            
        pdf_files = [f for f in os.listdir(self.corpus_path) if f.endswith('.pdf')]
        
        if pdf_files:
            documents = []
            for pdf in pdf_files:
                try:
                    loader = PyPDFLoader(os.path.join(self.corpus_path, pdf))
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {pdf}: {e}")
            
            if documents:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
                splits = text_splitter.split_documents(documents)
                
                self.vector_db = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory="chroma_db"
                )

    def _query_rag(self, query):
        if self.vector_db:
            docs = self.vector_db.similarity_search(query, k=3)
            return "\n".join([doc.page_content for doc in docs])
        return "Resmi prospektüs verisi bulunamadı."

    def _groq_agent(self, role, prompt, model="llama-3.3-70b-versatile"):
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"Sen uzman bir {role} birimisin. Kesin ve tıbbi doğrulukta Türkçe bilgi ver."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=0.1
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Agent Error: {str(e)}"

    def run_analysis(self, vision_data):
        try:
            if isinstance(vision_data, str):
                try:
                    vision_json = json.loads(vision_data)
                except:
                    return {"error": "Vision data parsing failure."}
            else:
                vision_json = vision_data

            drug_name = vision_json.get("commercial_name", "Bilinmeyen İlaç")
            active_ing = vision_json.get("active_ingredient", "")

            # 1. RAG Search
            rag_info = self._query_rag(f"{drug_name} {active_ing}")

            # 2. Safety Audit
            safety_prompt = f"İlaç: {drug_name}. Etken Madde: {active_ing}. Veri: {rag_info}. Kritik yan etkiler ve etkileşimleri Türkçe listele."
            safety_report = self._groq_agent("Safety-Auditor", safety_prompt)

            # 3. Deep Analysis (Groq Llama-3.1 70B instead of Gemini)
            analysis_prompt = f"{drug_name} ({active_ing}) hakkında detaylı farmakolojik bilgi ve üretici profili çıkar. Dil: Türkçe."
            corp_report = self._groq_agent("Corporate-Analyst", analysis_prompt)

            # 4. Final Synthesis
            synthesis_prompt = f"""
            Tüm verileri birleştirerek profesyonel bir tıbbi rapor oluştur. 
            DİL: TÜRKÇE.
            İLAÇ: {drug_name}
            BİLGİLER: {vision_json}
            RAG: {rag_info}
            GÜVENLİK: {safety_report}
            ANALİZ: {corp_report}
            
            Format:
            - İlaç Kimlik Özeti
            - Kullanım Amacı
            - Kritik Uyarılar (Vurgula)
            - Farmakolojik Detaylar
            - Kaynakça
            """
            final_report = self._groq_agent("Report-Synthesizer", synthesis_prompt)
            
            return {
                "summary": f"{drug_name} | {active_ing}",
                "indications": "Prospektüs verisine dayalı kullanım...",
                "warnings": safety_report,
                "details": corp_report,
                "sources": "PharmaGuard RAG Engine v2.0 (Groq-Powered)",
                "full_text": final_report
            }
        except Exception as e:
            return {"error": f"Orchestration failure: {str(e)}"}
