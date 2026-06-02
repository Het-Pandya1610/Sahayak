from FlagEmbedding import FlagReranker

import torch


reranker = FlagReranker(

    'BAAI/bge-reranker-base',

    use_fp16=True
)


def rerank_results(

    query,
    results
):

    if not results:

        return []


    pairs = []


    for result in results:

        scheme = result['scheme']


        text = f"""

        Scheme:
        {scheme['scheme_name']}

        Details:
        {scheme['details']}

        Benefits:
        {scheme['benefits']}

        Eligibility:
        {scheme['eligibility']}

        Category:
        {scheme['schemeCategory']}

        Tags:
        {", ".join(scheme['tags'])}

        Application:
        {scheme['application']}
        """


        pairs.append([

            query,
            text
        ])


    raw_scores = reranker.compute_score(
        pairs
    )


    reranked = []


    for idx, result in enumerate(results):


        normalized_score = torch.sigmoid(

            torch.tensor(raw_scores[idx])

        ).item()


        reranked.append({

            'rerank_score':
                float(normalized_score),

            'raw_score':
                float(raw_scores[idx]),

            'scheme':
                result['scheme']
        })


    reranked.sort(

        key=lambda x:
            x['rerank_score'],

        reverse=True
    )


    return reranked