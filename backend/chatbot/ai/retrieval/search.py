import pickle
import numpy as np # type: ignore
from chatbot.ai.embeddings.embedding_model import model
from schemes.models import Scheme

# Load vector store
with open(
    'chatbot/ai/vectorstore/vector_store.pkl',
    'rb'
) as f:
    data = pickle.load(f)
    embeddings = data['embeddings']
    metadata = data['metadata']


def semantic_search(query, top_k=10):
    """
    Perform semantic search and return Scheme objects with scores
    """
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )[0]

    similarities = np.dot(
        embeddings,
        query_embedding
    )

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for idx in top_indices:
        # Get the scheme data from metadata (it's a dict)
        scheme_data = metadata[idx]
        
        # Try to find the actual Scheme object from database
        # Use slug or scheme_name to find it
        scheme_obj = None
        
        # First try by slug
        if 'slug' in scheme_data and scheme_data['slug']:
            scheme_obj = Scheme.objects(slug=scheme_data['slug']).first()
        
        # If not found, try by scheme_name
        if not scheme_obj and 'scheme_name' in scheme_data:
            scheme_obj = Scheme.objects(scheme_name=scheme_data['scheme_name']).first()
        
        # If still not found, try case-insensitive search
        if not scheme_obj and 'scheme_name' in scheme_data:
            scheme_obj = Scheme.objects(scheme_name__icontains=scheme_data['scheme_name']).first()
        
        # If we found a Scheme object, use it; otherwise use the dict
        results.append({
            'score': float(similarities[idx]),
            'scheme': scheme_obj if scheme_obj else scheme_data
        })

    return results