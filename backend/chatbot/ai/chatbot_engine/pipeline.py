from chatbot.ai.retrieval.hybrid_search import hybrid_search

from chatbot.ai.reranker.rerank import rerank_results

from chatbot.ai.chatbot_engine.response_generator import generate_response


FINAL_THRESHOLD = 0.55


def chatbot_pipeline(

    query,
    history=None
):
    history = history or []


    print("QUERY:", query)


    results = hybrid_search(
        query
    )


    if not results:

        return {

            'success': False,

            'answer':
                'Sorry, I could not find any relevant government scheme.',

            'schemes': []
        }


    reranked = rerank_results(

        query,
        results
    )


    if not reranked:

        return {

            'success': False,

            'answer':
                'Sorry, I could not find any relevant government scheme.',

            'schemes': []
        }


    best_score = reranked[0]['rerank_score']


    print("BEST RERANK SCORE:", best_score)


    if best_score < FINAL_THRESHOLD:

        return {

            'success': False,

            'answer':
                'I only answer questions related to government schemes.',

            'confidence':
                round(best_score * 100, 2)
        }


    return generate_response(

        query,
        reranked,
        history
    )