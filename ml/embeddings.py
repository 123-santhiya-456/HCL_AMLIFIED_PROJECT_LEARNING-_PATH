"""
Embedding Engine using Sentence Transformers + FAISS.
Generates dense embeddings for courses/projects and enables
fast semantic similarity search.
"""
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple

# These are lazy-imported to handle missing dependencies gracefully
_st_model = None
_faiss_index = None
_resource_map: List[Dict] = []  # maps FAISS index → resource metadata

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
INDEX_PATH = os.path.join(DATA_DIR, "embeddings.idx")
MAP_PATH = os.path.join(DATA_DIR, "resource_map.pkl")


def _get_model():
    """Lazy-load the Sentence Transformers model."""
    global _st_model
    if _st_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("⏳ Loading sentence transformer model…")
            _st_model = SentenceTransformer(MODEL_NAME)
            print("✅ Model loaded.")
        except Exception as e:
            print(f"⚠️  Could not load SentenceTransformer: {e}")
            _st_model = None
    return _st_model


def embed_texts(texts: List[str]) -> Optional[np.ndarray]:
    """
    Generate embeddings for a list of texts.
    Returns numpy array of shape (N, EMBEDDING_DIM) or None on failure.
    """
    model = _get_model()
    if model is None:
        return None
    try:
        embeddings = model.encode(texts, normalize_embeddings=True,
                                  show_progress_bar=False)
        return np.array(embeddings, dtype=np.float32)
    except Exception as e:
        print(f"⚠️  Embedding error: {e}")
        return None


def build_index(resources: List[Dict]) -> bool:
    """
    Build FAISS index from a list of resource dicts.
    Each resource must have: id, title, description, skills (list), resource_type.
    Returns True on success.
    """
    global _faiss_index, _resource_map

    try:
        import faiss
    except ImportError:
        print("⚠️  faiss-cpu not installed. Semantic search disabled.")
        return False

    texts = []
    for res in resources:
        skills_str = ", ".join(res.get("skills", []))
        text = f"{res.get('title', '')} {res.get('description', '')} Skills: {skills_str}"
        texts.append(text)

    embeddings = embed_texts(texts)
    if embeddings is None:
        return False

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner-product (cosine on normalized vectors)
    index.add(embeddings)

    _faiss_index = index
    _resource_map = resources

    # Persist to disk
    faiss.write_index(index, INDEX_PATH)
    with open(MAP_PATH, "wb") as f:
        pickle.dump(resources, f)

    print(f"✅ FAISS index built: {index.ntotal} vectors indexed.")
    return True


def load_index() -> bool:
    """Load persisted FAISS index from disk."""
    global _faiss_index, _resource_map

    if not os.path.exists(INDEX_PATH) or not os.path.exists(MAP_PATH):
        return False

    try:
        import faiss
        _faiss_index = faiss.read_index(INDEX_PATH)
        with open(MAP_PATH, "rb") as f:
            _resource_map = pickle.load(f)
        print(f"✅ FAISS index loaded: {_faiss_index.ntotal} vectors.")
        return True
    except Exception as e:
        print(f"⚠️  Could not load FAISS index: {e}")
        return False


def semantic_search(query: str, top_k: int = 20) -> List[Dict]:
    """
    Find the most semantically similar resources for a query string.
    Returns list of resource dicts with added 'semantic_score' field.
    Falls back to empty list if FAISS/embedder unavailable.
    """
    global _faiss_index, _resource_map

    # Ensure index is loaded
    if _faiss_index is None:
        load_index()
    if _faiss_index is None or not _resource_map:
        return []

    query_emb = embed_texts([query])
    if query_emb is None:
        return []

    try:
        k = min(top_k, _faiss_index.ntotal)
        distances, indices = _faiss_index.search(query_emb, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(_resource_map):
                res = dict(_resource_map[idx])
                res["semantic_score"] = float(dist)
                results.append(res)
        return results
    except Exception as e:
        print(f"⚠️  FAISS search error: {e}")
        return []


def get_resource_embedding(resource: Dict) -> Optional[np.ndarray]:
    """Get embedding for a single resource."""
    skills_str = ", ".join(resource.get("skills", []))
    text = f"{resource.get('title', '')} {resource.get('description', '')} Skills: {skills_str}"
    embs = embed_texts([text])
    return embs[0] if embs is not None else None


def ensure_index_ready(courses: List[Dict], projects: List[Dict]) -> bool:
    """
    Initialize the FAISS index from DB resources if not already built.
    Safe to call multiple times — will load from disk if available.
    """
    if load_index():
        return True
    resources = courses + projects
    if not resources:
        return False
    return build_index(resources)
