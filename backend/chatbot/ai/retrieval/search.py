import pickle
import numpy as np # type: ignore

from chatbot.ai.embeddings.embedding_model import model


with open(
    'chatbot/ai/vectorstore/vector_store.pkl',
    'rb'
) as f:

    data = pickle.load(f)

    embeddings = data['embeddings']

    metadata = data['metadata']


def semantic_search(
    query,
    top_k=10
):

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

        results.append({

            'score':
                float(similarities[idx]),

            'scheme':
                metadata[idx]
        })


    return results