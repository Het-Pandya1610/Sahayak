from chatbot.ai.retrieval.hybrid_search import hybrid_search
from chatbot.ai.reranker.rerank import rerank_results
from chatbot.ai.chatbot_engine.response_generator import generate_response
from chatbot.ai.classifier.intent_detector import detect_intent

# Dynamic threshold based on intent
FINAL_THRESHOLD = 0.45  # Base threshold

def chatbot_pipeline(query, history=None):
    history = history or []

    # Enhanced intent detection with confidence
    intent, confidence = detect_intent(query, return_confidence=True)
    
    # Ensure confidence is Python float
    confidence = float(confidence)
    
    print(f"INTENT: {intent} (confidence: {confidence:.3f})")
    print(f"QUERY: {query}")

    # Social intents - always handle even with low confidence
    if intent in {"GREETING", "THANKS", "GOODBYE"}:
        response = generate_response(query, [], history)
        # Ensure all values are JSON serializable
        response['confidence'] = float(confidence)
        return response

    results = hybrid_search(query)

    if not results:
        return {
            'success': False,
            'answer': 'Sorry, I could not find any relevant government scheme. Could you please rephrase your query?',
            'schemes': [],
            'confidence': float(confidence)
        }

    reranked = rerank_results(query, results)

    if not reranked:
        return {
            'success': False,
            'answer': 'Sorry, I could not find any relevant government scheme.',
            'schemes': [],
            'confidence': 0.0
        }

    # Ensure scores are Python floats
    for item in reranked:
        if 'rerank_score' in item:
            item['rerank_score'] = float(item['rerank_score'])
        if 'raw_score' in item:
            item['raw_score'] = float(item['raw_score'])

    best_score = float(reranked[0]['rerank_score'])
    print(f"BEST RERANK SCORE: {best_score:.4f}")

    # Adaptive threshold based on intent
    if intent in ["ELIGIBILITY", "RECOMMENDATION"]:
        # More lenient for eligibility and recommendation queries
        adaptive_threshold = 0.35
    elif intent == "BENEFITS":
        adaptive_threshold = 0.40
    else:
        adaptive_threshold = FINAL_THRESHOLD

    if best_score < adaptive_threshold:
        # Provide helpful suggestion instead of rejection
        if intent == "ELIGIBILITY":
            return {
                'success': False,
                'answer': "I couldn't find specific schemes matching your eligibility criteria. Could you please provide more details like your state, category, or income level? This will help me find more relevant schemes.",
                'confidence': float(round(best_score * 100, 2)),
                'schemes': []
            }
        elif intent == "RECOMMENDATION":
            return {
                'success': False,
                'answer': "I need more information to recommend the best schemes. Could you share your state, category, and specific needs? This will help me suggest the most suitable schemes for you.",
                'confidence': float(round(best_score * 100, 2)),
                'schemes': []
            }
        else:
            return {
                'success': False,
                'answer': "I'm not confident about the relevance of the schemes found. Could you provide more specific details about what you're looking for?",
                'confidence': float(round(best_score * 100, 2)),
                'schemes': []
            }

    return generate_response(query, reranked, history)