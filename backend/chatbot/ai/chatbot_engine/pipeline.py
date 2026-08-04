from chatbot.ai.retrieval.hybrid_search import hybrid_search
from chatbot.ai.reranker.rerank import rerank_results
from chatbot.ai.chatbot_engine.response_generator import generate_response
from chatbot.ai.classifier.intent_detector import detect_intent
from chatbot.ai.classifier.user_profile_extractor import profile_extractor
from chatbot.ai.retrieval.filters import filter_and_rank

# Dynamic threshold based on intent
FINAL_THRESHOLD = 0.45

def chatbot_pipeline(query, history=None):
    history = history or []

    # Extract user profile from query
    user_profile = profile_extractor.extract(query)
    print(f"👤 USER PROFILE: {user_profile}")

    if user_profile.get('state'):
        print(f"📍 State detected: {user_profile['state']} (from query)")

    # Enhanced intent detection with confidence
    intent, confidence = detect_intent(query, return_confidence=True)
    
    # Ensure confidence is Python float
    confidence = float(confidence)
    
    print(f"INTENT: {intent} (confidence: {confidence:.3f})")
    print(f"QUERY: {query}")

    # Social intents - always handle even with low confidence
    if intent in {"GREETING", "THANKS", "GOODBYE"}:
        response = generate_response(query, [], history)
        response['confidence'] = float(confidence)
        return response

    # Search with profile context
    # Add profile context to search query for better results
    enhanced_query = query
    if user_profile.get('state'):
        enhanced_query += f" {user_profile['state']} state"
    if user_profile.get('category'):
        enhanced_query += f" {user_profile['category']} category"
    
    results = hybrid_search(enhanced_query)

    if not results:
        return {
            'success': False,
            'answer': 'Sorry, I could not find any relevant government scheme. Could you please rephrase your query with more details like your state, category, or education level?',
            'schemes': [],
            'confidence': float(confidence),
            'user_profile': user_profile
        }

    # Rerank results
    reranked = rerank_results(query, results)

    if not reranked:
        return {
            'success': False,
            'answer': 'Sorry, I could not find any relevant government scheme.',
            'schemes': [],
            'confidence': 0.0,
            'user_profile': user_profile
        }

    # Ensure scores are Python floats
    for item in reranked:
        if 'rerank_score' in item:
            item['rerank_score'] = float(item['rerank_score'])
        if 'raw_score' in item:
            item['raw_score'] = float(item['raw_score'])

    # Apply profile-based filtering and boosting
    boosted_results = filter_and_rank(reranked, user_profile, threshold=0.35)

    if not boosted_results:
        return {
            'success': False,
            'answer': "I couldn't find specific schemes matching your profile. Could you provide more details like your state, category, or education level? This will help me find more relevant schemes.",
            'confidence': 0.0,
            'user_profile': user_profile,
            'schemes': []
        }

    best_score = float(boosted_results[0].get('boosted_score', boosted_results[0].get('rerank_score', 0)))
    print(f"BEST SCORE: {best_score:.4f}")
    print(f"PROFILE MATCHES: {boosted_results[0].get('profile_matches', [])}")

    # Adaptive threshold
    if intent in ["ELIGIBILITY", "RECOMMENDATION"]:
        adaptive_threshold = 0.30
    elif intent == "BENEFITS":
        adaptive_threshold = 0.35
    else:
        adaptive_threshold = FINAL_THRESHOLD

    if best_score < adaptive_threshold:
        if user_profile.get('state') or user_profile.get('category'):
            return {
                'success': False,
                'answer': f"I found some schemes but they may not perfectly match your profile. Could you provide more details about your specific needs? This will help me find more accurate schemes for you.",
                'confidence': float(round(best_score * 100, 2)),
                'user_profile': user_profile,
                'schemes': []
            }
        else:
            return {
                'success': False,
                'answer': "I couldn't find specific schemes matching your criteria. Please provide details like your state, category, education level, or income to get personalized scheme recommendations.",
                'confidence': float(round(best_score * 100, 2)),
                'user_profile': user_profile,
                'schemes': []
            }

    # Generate response with user profile context
    response = generate_response(query, boosted_results, history, user_profile)
    response['user_profile'] = user_profile
    
    return response