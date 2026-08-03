from FlagEmbedding import FlagReranker
import torch
import numpy as np

reranker = FlagReranker(
    'BAAI/bge-reranker-base',
    use_fp16=True
)

def rerank_results(query, results):
    """Enhanced reranking with proper score scaling."""

    if not results:
        return []

    # Create pairs with enriched text
    pairs = []
    for result in results:
        scheme = result['scheme']
        
        # Enhanced text representation with proper weighting
        text = f"""
        Scheme: {scheme['scheme_name']}
        Category: {scheme['schemeCategory']}
        Level: {scheme['level']}
        Tags: {", ".join(scheme['tags'])}
        
        Details: {scheme['details']}
        
        Benefits: {scheme['benefits']}
        
        Eligibility: {scheme['eligibility']}
        
        Application: {scheme['application']}
        """
        
        pairs.append([query, text])

    raw_scores = reranker.compute_score(pairs)

    reranked = []
    for idx, result in enumerate(results):
        # Proper sigmoid scaling
        normalized_score = torch.sigmoid(torch.tensor(raw_scores[idx])).item()
        
        # Boost for high raw scores (relevance)
        boost = 1.0
        if raw_scores[idx] > 2.0:
            boost = 1.2
        elif raw_scores[idx] > 1.0:
            boost = 1.1
            
        # Field-specific boosts
        scheme = result['scheme']
        query_terms = set(query.lower().split())
        
        # Check important fields
        important_fields = [
            scheme['scheme_name'].lower(),
            ' '.join(scheme['tags']).lower(),
            scheme['schemeCategory'].lower()
        ]
        
        # Count query term matches in important fields
        matches = 0
        for field in important_fields:
            for term in query_terms:
                if term in field:
                    matches += 1
                    break
        
        if matches > 0:
            boost += 0.05 * matches
        
        # Final calibrated score - ensure it doesn't exceed 1.0
        calibrated_score = min(normalized_score * boost, 0.99)
        
        reranked.append({
            'rerank_score': calibrated_score,
            'raw_score': float(raw_scores[idx]),
            'scheme': result['scheme']
        })

    # Sort by calibrated score
    reranked.sort(key=lambda x: x['rerank_score'], reverse=True)

    return reranked