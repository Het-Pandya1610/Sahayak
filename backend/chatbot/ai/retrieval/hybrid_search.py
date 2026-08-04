from chatbot.ai.retrieval.search import semantic_search
from chatbot.ai.retrieval.query_cleaner import clean_query
from chatbot.ai.retrieval.filters import filter_results
from schemes.models import Scheme

def hybrid_search(query):
    """
    Hybrid search combining semantic search with exact slug matching
    """
    # First check for exact slug match
    query_lower = query.lower().strip()
    slug_match = Scheme.objects(slug=query_lower).first()
    
    if slug_match:
        print(f"✅ Found exact slug match: {slug_match.scheme_name}")
        return [{
            'score': 1.0,
            'scheme': slug_match
        }]
    
    # Check for scheme name match
    name_match = Scheme.objects(scheme_name__icontains=query).first()
    if name_match:
        print(f"✅ Found name match: {name_match.scheme_name}")
        return [{
            'score': 0.95,
            'scheme': name_match
        }]
    
    # Otherwise, do semantic search
    cleaned_query = clean_query(query)
    results = semantic_search(cleaned_query)
    
    # Filter results with threshold
    filtered_results = filter_results(results, threshold=0.35)
    
    # Ensure all results have 'score' key
    for result in filtered_results:
        if 'rerank_score' not in result and 'boosted_score' not in result:
            # Use the original score from semantic search
            result['score'] = result.get('score', 0.0)
    
    return filtered_results