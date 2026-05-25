from FlagEmbedding import FlagReranker


reranker = FlagReranker(

    'BAAI/bge-reranker-large',

    use_fp16=True
)


def rerank_results(
    query,
    results
):

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
        """


        pairs.append([

            query,

            text
        ])


    scores = reranker.compute_score(
        pairs
    )


    reranked = []


    for idx, result in enumerate(results):

        reranked.append({

            'rerank_score':
                float(scores[idx]),

            'scheme':
                result['scheme']
        })


    reranked.sort(

        key=lambda x:
            x['rerank_score'],

        reverse=True
    )


    return reranked