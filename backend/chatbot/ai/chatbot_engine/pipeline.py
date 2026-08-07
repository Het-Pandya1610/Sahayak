from chatbot.ai.retrieval.hybrid_search import hybrid_search
from chatbot.ai.reranker.rerank import rerank_results
from chatbot.ai.chatbot_engine.response_generator import generate_response
from chatbot.ai.classifier.intent_detector import detect_intent
from chatbot.ai.classifier.user_profile_extractor import profile_extractor
from chatbot.ai.retrieval.filters import filter_and_rank
from chatbot.ai.memory.conversation_memory import get_conversation_memory

# Dynamic threshold based on intent
FINAL_THRESHOLD = 0.45

def chatbot_pipeline(query, history=None):
    history = history or []
    
    # Get conversation memory
    memory = get_conversation_memory()
    
    # Build context string for the query
    context_string = memory.build_context_string()
    
    # Check if this is a follow-up question
    follow_up_context = memory.get_follow_up_context(query)
    
    print(f"🔍 FOLLOW-UP DETECTION: {follow_up_context}")
    
    # ============================================================
    # HANDLE FOLLOW-UP QUESTIONS
    # ============================================================
    if follow_up_context.get('is_follow_up') and follow_up_context.get('needs_scheme_reference'):
        # Try to get scheme from previous context
        scheme_number = follow_up_context.get('referenced_scheme')
        last_schemes = memory.get_last_schemes()
        
        if scheme_number and last_schemes:
            # User specified a scheme number
            scheme_index = scheme_number - 1
            if 0 <= scheme_index < len(last_schemes):
                referenced_scheme = last_schemes[scheme_index]
                print(f"📌 User referred to scheme #{scheme_number}: {referenced_scheme.get('scheme_name', 'Unknown')}")
                
                # Create a new query that includes the scheme name
                scheme_name = referenced_scheme.get('scheme_name', '')
                # Check what the user wants to know
                if follow_up_context.get('referenced_intent') == 'APPLICATION':
                    enhanced_query = f"How to apply for {scheme_name}"
                elif follow_up_context.get('referenced_intent') == 'ELIGIBILITY':
                    enhanced_query = f"What is the eligibility for {scheme_name}"
                elif follow_up_context.get('referenced_intent') == 'BENEFITS':
                    enhanced_query = f"What are the benefits of {scheme_name}"
                else:
                    enhanced_query = f"Tell me about {scheme_name}"
                
                print(f"🔄 Enhanced query: {enhanced_query}")
                query = enhanced_query
                
                # Pass the specific scheme to search
                results = [{
                    'score': 1.0,
                    'scheme': referenced_scheme,
                    'rerank_score': 1.0
                }]
                
                # Generate response with context
                intent = follow_up_context.get('referenced_intent') or 'SCHEME_SEARCH'
                user_profile = profile_extractor.extract(query)
                
                response = generate_response(query, results, history, user_profile)
                response['follow_up'] = True
                response['referenced_scheme'] = scheme_name
                
                # Update memory with this interaction
                memory.add_message('user', query)
                memory.add_message('assistant', response.get('answer', ''))
                memory.update_context(query, intent, results)
                
                return response
        
        elif last_schemes and len(last_schemes) == 1:
            # Only one scheme in context, use it
            referenced_scheme = last_schemes[0]
            print(f"📌 Using only scheme in context: {referenced_scheme.get('scheme_name', 'Unknown')}")
            
            scheme_name = referenced_scheme.get('scheme_name', '')
            if follow_up_context.get('referenced_intent') == 'APPLICATION':
                enhanced_query = f"How to apply for {scheme_name}"
            elif follow_up_context.get('referenced_intent') == 'ELIGIBILITY':
                enhanced_query = f"What is the eligibility for {scheme_name}"
            elif follow_up_context.get('referenced_intent') == 'BENEFITS':
                enhanced_query = f"What are the benefits of {scheme_name}"
            else:
                enhanced_query = f"Tell me about {scheme_name}"
            
            query = enhanced_query
            results = [{
                'score': 1.0,
                'scheme': referenced_scheme,
                'rerank_score': 1.0
            }]
            
            intent = follow_up_context.get('referenced_intent') or 'SCHEME_SEARCH'
            user_profile = profile_extractor.extract(query)
            
            response = generate_response(query, results, history, user_profile)
            response['follow_up'] = True
            response['referenced_scheme'] = scheme_name
            
            memory.add_message('user', query)
            memory.add_message('assistant', response.get('answer', ''))
            memory.update_context(query, intent, results)
            
            return response

    # ============================================================
    # EXTRACT USER PROFILE
    # ============================================================
    user_profile = profile_extractor.extract(query)
    print(f"👤 USER PROFILE: {user_profile}")

    if user_profile.get('state'):
        print(f"📍 State detected: {user_profile['state']} (from query)")

    # ============================================================
    # INTENT DETECTION
    # ============================================================
    intent, confidence = detect_intent(query, return_confidence=True)
    confidence = float(confidence)
    
    print(f"INTENT: {intent} (confidence: {confidence:.3f})")
    print(f"QUERY: {query}")

    # Social intents - always handle even with low confidence
    if intent in {"GREETING", "THANKS", "GOODBYE"}:
        response = generate_response(query, [], history)
        response['confidence'] = float(confidence)
        
        # Update memory
        memory.add_message('user', query)
        memory.add_message('assistant', response.get('answer', ''))
        memory.update_context(query, intent)
        
        return response

    # ============================================================
    # SEARCH WITH CONTEXT
    # ============================================================
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

    # ============================================================
    # RERANK AND FILTER
    # ============================================================
    reranked = rerank_results(query, results)

    if not reranked:
        return {
            'success': False,
            'answer': 'Sorry, I could not find any relevant government scheme.',
            'schemes': [],
            'confidence': 0.0,
            'user_profile': user_profile
        }

    for item in reranked:
        if 'rerank_score' in item:
            item['rerank_score'] = float(item['rerank_score'])
        if 'raw_score' in item:
            item['raw_score'] = float(item['raw_score'])

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

    # ============================================================
    # ADAPTIVE THRESHOLD
    # ============================================================
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

    # ============================================================
    # GENERATE RESPONSE
    # ============================================================
    response = generate_response(query, boosted_results, history, user_profile)
    response['user_profile'] = user_profile
    
    # Store schemes in memory for follow-up questions
    scheme_list = []
    for item in boosted_results[:5]:
        scheme = item.get('scheme', {})
        if isinstance(scheme, dict):
            scheme_list.append(scheme)
        else:
            scheme_list.append({
                'scheme_name': getattr(scheme, 'scheme_name', 'Unknown'),
                'details': getattr(scheme, 'details', ''),
                'benefits': getattr(scheme, 'benefits', ''),
                'eligibility': getattr(scheme, 'eligibility', ''),
                'application': getattr(scheme, 'application', ''),
                'documents': getattr(scheme, 'documents', ''),
                'schemeCategory': getattr(scheme, 'schemeCategory', ''),
                'level': getattr(scheme, 'level', '')
            })
    
    # Update memory
    memory.add_message('user', query)
    memory.add_message('assistant', response.get('answer', ''))
    memory.update_context(query, intent, scheme_list, user_profile)
    
    return response