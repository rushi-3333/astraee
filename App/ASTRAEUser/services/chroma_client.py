import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from django.conf import settings

# Paths
CHROMA_DB_PATH = os.path.join(settings.BASE_DIR, 'Model', 'chroma_db')
LOCAL_MODEL_PATH = os.path.join(settings.BASE_DIR, 'Model', 'embeddings_model')

# Singleton instances
_client = None
_embedding_fn = None

def _ensure_local_model_exists():
    """Detects if model weights exist locally. Downloads and saves them if missing."""
    if not os.path.exists(LOCAL_MODEL_PATH) or not os.listdir(LOCAL_MODEL_PATH):
        print("[ASTRAE] Local embedding weights not found. Downloading 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        model.save(LOCAL_MODEL_PATH)
        print(f"[ASTRAE] Model weights successfully saved to {LOCAL_MODEL_PATH}")

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client

def get_embedding_function():
    global _embedding_fn
    if _embedding_fn is None:
        # 1. Detect and download if weights are missing
        _ensure_local_model_exists()
        
        # 2. Block online network checks for subsequent loads
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"

        # 3. Load embedding function directly from local disk directory
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=LOCAL_MODEL_PATH
        )
    return _embedding_fn

def get_collection(collection_name):
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    return client.get_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )