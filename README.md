# ⚖️ Intelligence Artificielle Juridique Mauritanienne (RAG Agentique v4.2)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-black?style=for-the-badge&logo=chroma&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama%203-orange?style=for-the-badge&logo=ai&logoColor=white)

> **Un moteur de recherche juridique intelligent et conversationnel, propulsé par une architecture multi-agents.**

---

## 🌟 À Propos

Ce projet révolutionne l'accès au **Journal Officiel de la Mauritanie** (ami.mr). Grâce à une architecture **RAG (Retrieval-Augmented Generation)** avancée, il permet aux professionnels du droit et aux citoyens de poser des questions naturelles et d'obtenir des réponses précises, sourcées et contextualisées.

Le système ne se contente pas de chercher des mots-clés : il **comprend**, **analyse**, et **synthétise** l'information juridique complexe.

---

## 🧠 Architecture Agentique (Le Cerveau)

Ce n'est pas un simple chatbot. C'est une équipe de **4 agents spécialisés** qui travaillent de concert pour vous répondre :

### 1. 🎯 **L'Orchestrator Agent**
*   **Mission :** Chef d'orchestre.
*   **Action :** Analyse votre question, comprend le contexte de la conversation et résout les ambiguïtés (ex: "il" ou "l'article précédent").

### 2. 🔍 **The Search Agent**
*   **Mission :** Bibliothécaire expert.
*   **Action :** Scanne instantanément plus de **40 000 segments** de textes juridiques dans ChromaDB pour trouver les articles de loi pertinents.

### 3. 🌐 **The Web Fallback Agent**
*   **Mission :** Éclaireur externe.
*   **Action :** Si la base de données interne ne suffit pas (confiance < 60%), il explore le web en temps réel via DuckDuckGo pour compléter l'information.

### 4. ✍️ **The Synthesis Agent**
*   **Mission :** Rédacteur juridique.
*   **Action :** Utilise la puissance de **Llama 3 (via Groq)** pour rédiger une réponse claire, structurée et professionnelle, en citant systématiquement ses sources.

---

## ✨ Fonctionnalités Clés

*   **💬 Mémoire Conversationnelle :** Posez des questions de suivi ("Et pour l'année 2023 ?"), l'IA se souvient du contexte.
*   **📅 Filtres Temporels :** Ciblez vos recherches sur des années spécifiques (2017-2025).
*   **📊 Transparence Totale :**
    *   Score de confiance pour chaque réponse.
    *   Lien direct vers les sources PDF.
    *   Statistiques de session en temps réel.
*   **🔌 Performance :** Réponses ultra-rapides grâce à l'inférence Groq.

---

## 🚀 Installation & Démarrage

### Pré-requis
*   Python 3.9+
*   Clé API [Groq](https://groq.com/) (gratuite en version bêta)

### 1. Cloner le projet
```bash
git clone https://github.com/Baba103/Projet-IA-generative.git
cd Projet-IA-generative
```

### 2. Installer les dépendances
```bash
pip install streamlit chromadb sentence-transformers groq bs4 requests
```

### 3. Configurer les clés
*Ouvrez `app_rag_agentique.py` et configurez votre `GROQ_API_KEY` (ou utilisez un fichier .env pour plus de sécurité).*

### 4. Lancer l'application
```bash
streamlit run app_rag_agentique.py
```

---

## 📂 Structure du Projet

```
Projet-IA-generative/
├── 📂 RAG_Cache_Incremental/   # Base de données vectorielle (ChromaDB)
├── 📂 Datasets_journal-officiel/ # Documents PDF sources (via LFS)
├── 📄 app_rag_agentique.py     # Application Streamlit principale
├── 📄 _RAG_Juridique_Final_.ipynb # Notebook de construction du RAG
└── 📄 README.md                # Documentation
```

---

## 📊 Données Techniques

| Métrique | Valeur |
| :--- | :--- |
| **Documents Indexés** | ~224 Livres/PDFs |
| **Chunks Vectoriels** | > 40,000 |
| **Période Couverte** | 2017 - 2025 |
| **Modèle d'Embedding** | `all-MiniLM-L6-v2` |
| **LLM** | `Llama-3.3-70b-versatile` |

---

<div align="center">

**Fait avec ❤️ pour la Justice Mauritanienne**

</div>
