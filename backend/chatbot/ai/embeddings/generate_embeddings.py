import pickle
import faiss
import numpy as np

from schemes.models import Scheme

from chatbot.ai.embeddings.embedding_model import model


def generate_embeddings():

    schemes = Scheme.objects.all()

    documents = []

    metadata = []


    for scheme in schemes:

        text = f"""

        Scheme Name:
        {scheme.scheme_name}

        Category:
        {scheme.schemeCategory}

        Tags:
        {", ".join(scheme.tags)}

        Details:
        {scheme.details}

        Benefits:
        {scheme.benefits}

        Eligibility:
        {scheme.eligibility}

        Application:
        {scheme.application}

        Documents:
        {scheme.documents}
        """


        text = text[:4000]


        documents.append(text)


        metadata.append({

            'id':
                str(scheme.id),

            'scheme_name':
                scheme.scheme_name,

            'details':
                scheme.details,

            'benefits':
                scheme.benefits,

            'eligibility':
                scheme.eligibility,

            'application':
                scheme.application,

            'documents':
                scheme.documents,

            'level':
                scheme.level,

            'schemeCategory':
                scheme.schemeCategory,

            'tags':
                scheme.tags
        })


    embeddings = model.encode(

        documents,

        batch_size=4,

        show_progress_bar=True,

        convert_to_numpy=True,

        normalize_embeddings=True
    )


    dimension = embeddings.shape[1]


    index = faiss.IndexFlatIP(dimension)


    index.add(
        np.array(
            embeddings,
            dtype=np.float32
        )
    )


    faiss.write_index(

        index,

        'chatbot/ai/vectorstore/faiss_index.bin'
    )


    with open(

        'chatbot/ai/vectorstore/vector_store.pkl',

        'wb'

    ) as f:

        pickle.dump({
            'embeddings':
                embeddings,
            'metadata':
                metadata
        }, f)


    print(
        f'Generated embeddings for {len(documents)} schemes'
    )