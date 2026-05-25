from chatbot.ai.retrieval.search import semantic_search

from chatbot.ai.retrieval.query_cleaner import clean_query

from chatbot.ai.retrieval.filters import filter_results


def hybrid_search(
    query
):

    cleaned_query = clean_query(
        query
    )


    results = semantic_search(
        cleaned_query
    )


    filtered_results = filter_results(
        results
    )


    return filtered_results