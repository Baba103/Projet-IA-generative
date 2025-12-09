# Script de vérification du cache

import chromadb
import os

CACHE_PATH = "C:/Users/hp/OneDrive/Desktop/dq/RAG_Cache_Incremental"

print("🔍 Vérification du cache...")
print("="*60)

# Vérifier que le dossier existe
if not os.path.exists(CACHE_PATH):
    print(f"❌ Dossier non trouvé: {CACHE_PATH}")
    exit(1)

print(f"✅ Dossier trouvé: {CACHE_PATH}")

# Vérifier chroma_db
chroma_path = os.path.join(CACHE_PATH, "chroma_db")
if not os.path.exists(chroma_path):
    print(f"❌ chroma_db non trouvé dans le cache")
    exit(1)

print(f"✅ chroma_db trouvé")

# Charger ChromaDB
try:
    client = chromadb.PersistentClient(path=chroma_path)
    print("✅ Client ChromaDB chargé")
except Exception as e:
    print(f"❌ Erreur chargement ChromaDB: {e}")
    exit(1)

# Lister collections
collections = client.list_collections()

print(f"\n📊 Collections disponibles: {len(collections)}")
print("="*60)

if len(collections) == 0:
    print("❌ Aucune collection trouvée dans le cache!")
    print("💡 Le cache est peut-être vide ou corrompu")
else:
    for i, col in enumerate(collections, 1):
        print(f"\n{i}. Nom: {col.name}")
        print(f"   Documents: {col.count():,}")
        print(f"   Métadonnées: {col.metadata}")

print("\n" + "="*60)
print("✅ Vérification terminée")
