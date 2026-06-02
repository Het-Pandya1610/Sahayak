from chatbot.ai.retrieval.hybrid_search import hybrid_search

from chatbot.ai.reranker.rerank import rerank_results


FINAL_THRESHOLD = 0.4


def is_scheme_related(query, context=""):


    enhanced_query = f"""

    Previous conversation:
    {context}

    Current user query:
    {query}
    """


    results = hybrid_search(enhanced_query)


    if not results:

        return (

            False,
            0.0
        )


    reranked = rerank_results(

        enhanced_query,
        results
    )


    if not reranked:

        return (

            False,
            0.0
        )


    best_score = reranked[0][
        'rerank_score'
    ]

    
    print("BEST RERANK SCORE:", best_score)

    return (

        best_score >= FINAL_THRESHOLD,

        float(best_score)
    )