# 🎨 Interface Streamlit COMPLÈTE avec Architecture Agentique - RAG v4.2

import streamlit as st
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import deque

# Configuration
st.set_page_config(
    page_title="RAG Multi-Documents Agentique",
    page_icon="🤖",
    layout="wide"
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

CACHE_PATH = "C:/Users/hp/OneDrive/Desktop/dq/RAG_Cache_Incremental"
GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════
# CLASSES AGENTIQUES
# ═══════════════════════════════════════════════════════════════════════════

class ConversationMemory:
    def __init__(self, max_turns=10):
        self.max_turns = max_turns
        self.history = deque(maxlen=max_turns)
    
    def add(self, question, answer):
        self.history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context(self, n=3):
        recent = list(self.history)[-n:]
        context = []
        for turn in recent:
            context.append(f"Q: {turn['question']}\\nR: {turn['answer'][:200]}")
        return "\\n\\n".join(context)
    
    def clear(self):
        self.history.clear()

class EntityTracker:
    def __init__(self):
        self.last_mentioned = {}
        self.mention_order = []
    
    def extract_entities(self, text):
        # Articles
        articles = re.findall(r'[Aa]rticle\\s+(\\d+)', text)
        if articles:
            self.last_mentioned["article"] = articles[-1]
            self.mention_order.append(("article", articles[-1]))
        
        # Directions/Services
        directions = re.findall(r'(?:Direction|Service)\\s+(?:de\\s+)?(?:la\\s+)?([A-ZÀ-ÿ\\s]+)', text)
        cleaned = [d.strip() for d in directions if len(d.strip()) > 3]
        if cleaned:
            self.last_mentioned["direction"] = cleaned[-1]
            self.mention_order.append(("direction", cleaned[-1]))
    
    def resolve(self, pronoun):
        p = pronoun.lower()
        if p in ["il", "elle", "le", "la"]:
            for etype in ["article", "direction"]:
                if etype in self.last_mentioned:
                    return f"{etype.capitalize()} {self.last_mentioned[etype]}"
        return pronoun
    
    def get_first(self):
        if self.mention_order:
            etype, value = self.mention_order[0]
            return f"{etype.capitalize()} {value}"
        return ""

# ═══════════════════════════════════════════════════════════════════════════
# INITIALISATION RAG
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def init_rag():
    """Initialiser système RAG agentique"""
    from sentence_transformers import SentenceTransformer
    import chromadb
    from groq import Groq
    
    with st.spinner("🔌 Chargement système agentique..."):
        # ChromaDB
        chroma_path = os.path.join(CACHE_PATH, "chroma_db")
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_collection(name="journal_officiel_incremental")
        
        # Embedding
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        
    return collection, embedding_model, groq_client

try:
    collection, embedding_model, groq_client = init_rag()
    st.success(f"✅ Système agentique chargé: {collection.count():,} documents")
except Exception as e:
    st.error(f"❌ Erreur: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory(max_turns=10)

if "entity_tracker" not in st.session_state:
    st.session_state.entity_tracker = EntityTracker()

if "stats" not in st.session_state:
    st.session_state.stats = {
        "questions": 0,
        "avg_confidence": 0,
        "coreferences_resolved": 0,
        "web_fallbacks": 0,
        "start_time": datetime.now()
    }

# ═══════════════════════════════════════════════════════════════════════════
# AGENTS RAG
# ═══════════════════════════════════════════════════════════════════════════

def orchestrator_agent(question, memory, entity_tracker):
    """Agent Orchestrateur - Enrichissement et résolution coréférences"""
    
    context = memory.get_context(n=2)
    
    # Détecter pronoms
    pronouns_pattern = r'\\b(il|elle|le|la|ses|premier|première|dernier|dernière)\\b'
    pronouns = re.findall(pronouns_pattern, question, re.IGNORECASE)
    
    enriched = question
    resolutions = {}
    
    for pronoun in pronouns:
        p = pronoun.lower()
        if p in ["premier", "première"]:
            resolution = entity_tracker.get_first()
        else:
            resolution = entity_tracker.resolve(pronoun)
        
        if resolution and resolution != pronoun:
            enriched = enriched.replace(pronoun, resolution)
            resolutions[pronoun] = resolution
    
    entity_tracker.extract_entities(question + " " + enriched)
    
    return enriched, context, resolutions

def search_agent(query, year=None, source=None, top_k=10):
    """Agent de Recherche - Recherche sémantique dans base"""
    
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    
    where_filter = {}
    if year:
        where_filter["year"] = str(year)
    if source:
        where_filter["source_file"] = {"$contains": source}
    
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
        where=where_filter if where_filter else None
    )
    
    if not results["documents"][0]:
        return [], 0.0
    
    docs = []
    distances = results["distances"][0]
    scores = [1 / (1 + d) for d in distances]
    confidence = sum(scores) / len(scores)
    
    for doc, meta, score in zip(results["documents"][0], results["metadatas"][0], scores):
        docs.append({
            "text": doc,
            "source": meta.get("source_file", "Unknown"),
            "year": meta.get("year", ""),
            "score": score,
            "metadata": meta
        })
    
    return docs, confidence

def web_fallback_agent(question):
    """Agent Web Fallback - Recherche DuckDuckGo si confiance faible"""
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Recherche DuckDuckGo
        url = f"https://html.duckduckgo.com/html/?q={question}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a', limit=3)
            
            web_results = []
            for result in results:
                title = result.get_text()
                link = result.get('href', '')
                web_results.append({"title": title, "link": link})
            
            return web_results
        
    except Exception as e:
        pass
    
    return []

def synthesis_agent(question, docs, context):
    """Agent de Synthèse - Génération réponse avec Groq"""
    
    context_str = "\\n\\n".join([f"[Doc {i}] {d['text'][:500]}" for i, d in enumerate(docs[:5], 1)])
    
    prompt = f"""Tu es un assistant juridique expert.

SOURCES DOCUMENTAIRES:
{context_str}

CONTEXTE CONVERSATIONNEL:
{context[:300] if context else 'Aucun'}

QUESTION: {question}

INSTRUCTIONS:
- Réponds de manière précise et structurée
- Utilise des points • pour les listes
- Cite les sources quand pertinent
- Si info manquante, indique-le clairement

RÉPONSE:"""
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur Groq: {e}"

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    # Filtres
    st.markdown("### 🔍 Filtres")
    year = st.selectbox("📅 Année", ["Toutes"] + [str(y) for y in range(2025, 2016, -1)])
    source = st.text_input("📄 Source", placeholder="Ex: 1389")
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Session")
    st.metric("Questions", st.session_state.stats["questions"])
    
    if st.session_state.stats["questions"] > 0:
        avg = st.session_state.stats["avg_confidence"] / st.session_state.stats["questions"]
        st.metric("Confiance Moy.", f"{avg:.0%}")
    
    st.metric("Coréférences", st.session_state.stats["coreferences_resolved"])
    st.metric("Fallbacks Web", st.session_state.stats["web_fallbacks"])
    
    duration = (datetime.now() - st.session_state.stats["start_time"]).seconds // 60
    st.caption(f"⏱️ Session: {duration} min")
    
    st.markdown("---")
    
    if st.button("🔄 Nouvelle Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_memory.clear()
        st.session_state.entity_tracker = EntityTracker()
        st.rerun()
    
    st.markdown("---")
    
    with st.expander("🤖 Architecture Agentique"):
        st.markdown("""
        **Agents Actifs:**
        
        1. 🎯 **Orchestrator**
           - Enrichissement contexte
           - Résolution coréférences
           
        2. 🔍 **Search Agent**
           - Recherche sémantique
           - Calcul confiance
           
        3. 🌐 **Web Fallback**
           - Si confiance < 50%
           - DuckDuckGo
           
        4. ✍️ **Synthesis Agent**
           - Génération Groq
           - Citations sources
        """)
    
    with st.expander("ℹ️ À Propos"):
        st.markdown("""
        **RAG Agentique v4.2**
        
        - 📚 ~224 PDFs
        - 📊 40,021 chunks
        - 📅 2017-2025
        - 🤖 4 agents spécialisés
        """)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

st.title("🤖 RAG Multi-Documents Agentique")
st.caption("💻 Architecture avec 4 Agents Spécialisés | Mémoire Conversationnelle | Résolution Coréférences")

# Historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if "meta" in msg and msg["role"] == "assistant":
            cols = st.columns(4)
            cols[0].caption(f"📊 {msg['meta']['conf']:.0%}")
            cols[1].caption(f"📄 {msg['meta']['sources']} sources")
            cols[2].caption(f"⏱️ {msg['meta']['time']:.1f}s")
            if msg['meta'].get('coreferences'):
                cols[3].caption(f"🔄 {len(msg['meta']['coreferences'])} coréf.")

# Input
if prompt := st.chat_input("💬 Votre question..."):
    
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        status_placeholder = st.empty()
        
        start = time.time()
        
        # 1. Orchestration
        status_placeholder.info("🎯 Orchestrator: Enrichissement question...")
        enriched_q, context, resolutions = orchestrator_agent(
            prompt, 
            st.session_state.conversation_memory,
            st.session_state.entity_tracker
        )
        
        if resolutions:
            status_placeholder.success(f"🔄 Coréférences résolues: {resolutions}")
            st.session_state.stats["coreferences_resolved"] += len(resolutions)
            time.sleep(1)
        
        # 2. Recherche
        status_placeholder.info("🔍 Search Agent: Recherche dans base...")
        year_param = None if year == "Toutes" else year
        source_param = source if source else None
        docs, confidence = search_agent(enriched_q, year_param, source_param)
        
        # 3. Fallback Web si confiance faible OU aucun résultat
        web_used = False
        if (confidence < 0.6 or not docs):  # ← Seuil augmenté à 60% + activation si vide
            status_placeholder.warning("🌐 Web Fallback: Confiance faible ou pas de résultats, recherche web...")
            web_results = web_fallback_agent(prompt)
            if web_results:
                web_used = True
                st.session_state.stats["web_fallbacks"] += 1
                # Afficher résultats web
                with st.expander("🌐 Résultats Web"):
                    for i, res in enumerate(web_results, 1):
                        st.write(f"{i}. [{res['title']}]({res['link']})")
                time.sleep(1)
        
        # 4. Synthèse
        if docs:
            status_placeholder.info("✍️ Synthesis Agent: Génération réponse...")
            answer = synthesis_agent(prompt, docs, context)
            exec_time = time.time() - start
            
            # Affichage
            status_placeholder.empty()
            placeholder.markdown(answer)
            
            cols = st.columns(4)
            color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
            cols[0].caption(f"{color} {confidence:.0%}")
            cols[1].caption(f"📄 {len(docs)} sources")
            cols[2].caption(f"⏱️ {exec_time:.1f}s")
            if resolutions:
                cols[3].caption(f"🔄 {len(resolutions)} coréf.")
            
            if web_used:
                st.info("🌐 Fallback web activé (confiance initiale faible)")
            
            # Sauvegarder
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "meta": {
                    "conf": confidence,
                    "sources": len(docs),
                    "time": exec_time,
                    "coreferences": resolutions
                }
            })
            
            # Mémoire
            st.session_state.conversation_memory.add(prompt, answer)
            st.session_state.entity_tracker.extract_entities(prompt + " " + answer)
            
            # Stats
            st.session_state.stats["questions"] += 1
            st.session_state.stats["avg_confidence"] += confidence
            
        else:
            status_placeholder.empty()
            placeholder.error("❌ Aucun résultat trouvé")
