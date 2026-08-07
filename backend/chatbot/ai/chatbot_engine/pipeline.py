from chatbot.ai.retrieval.hybrid_search import hybrid_search
from chatbot.ai.reranker.rerank import rerank_results
from chatbot.ai.chatbot_engine.response_generator import generate_response, _build_follow_up_response, clean_emoji, get_scheme_attr
from chatbot.ai.classifier.intent_detector import detect_intent
from chatbot.ai.classifier.user_profile_extractor import profile_extractor
from chatbot.ai.retrieval.filters import filter_and_rank
from chatbot.ai.memory.conversation_memory import get_conversation_memory

# Dynamic threshold based on intent
FINAL_THRESHOLD = 0.45

def extract_scheme_name_from_response(content: str):
    """
    Extract scheme name from assistant response content.
    Skips section headers and ignores common patterns.
    Returns the LAST scheme name found (most recent)
    """
    if not content:
        return None
    
    lines = content.split('\n')
    
    # Patterns to skip (section headers, common phrases)
    ignore_patterns = [
        'Application Process for',
        'Eligibility Criteria for',
        'Benefits of',
        'Required Documents for',
        'Step-by-Step Guide',
        'Next Steps:',
        'To apply for:',
        'Would you like',
        'Check if you meet',
        'Information not available',
        'Important Tips:',
        'Additional Details:',
        'Category:',
        'Level:',
        'Apply before',
        'Keep all documents',
        'Double-check all',
        'Save your application',
        'Need more help',
        'Any specific aspect',
        'Based on your',
        'Which scheme',
        '--- SCHEME',
        '---',
        '**[',
        '**(',
        '--- SCHEME ---',
    ]
    
    # Phrases that indicate a section header (skip these)
    skip_phrases = [
        'Application Process', 'Eligibility Criteria', 'Benefits of',
        'Step-by-Step', 'Required Documents', 'Next Steps', 'About',
        'To apply for', 'Based on your', 'Which scheme', 'Details of',
        'Important Tips', 'Additional Details', 'How to Access',
        'Information not available', 'Not specified'
    ]
    
    # Store all found scheme names (latest one will be kept)
    found_names = []
    
    for line in lines:
        line_clean = line.strip()
        
        if not line_clean:
            continue
        
        # Skip if it's an ignore pattern
        should_ignore = False
        for pattern in ignore_patterns:
            if pattern in line_clean:
                should_ignore = True
                break
        
        if should_ignore:
            continue
        
        # Check if line looks like a scheme name
        # Pattern 1: Starts with # or **
        if line_clean.startswith('#') or line_clean.startswith('**'):
            potential_name = line_clean
            
            # Remove markdown
            potential_name = potential_name.replace('#', '').replace('**', '').strip()
            
            # Remove common suffixes
            suffixes = [' - Key Information', ' - Complete Details', ' -', '—', ' (', '[']
            for suffix in suffixes:
                if suffix in potential_name:
                    potential_name = potential_name.split(suffix)[0].strip()
                    break
            
            # Skip short names
            if len(potential_name) < 5:
                continue
            
            # Skip if it's a section header
            is_skip = False
            for phrase in skip_phrases:
                if phrase.lower() in potential_name.lower():
                    is_skip = True
                    break
            
            if is_skip:
                continue
            
            # Skip if it contains section indicators
            section_indicators = ['Process', 'Criteria', 'Benefits', 'Documents', 'Steps', 'Tips', 'Guide']
            is_section = False
            for indicator in section_indicators:
                if indicator.lower() in potential_name.lower() and len(potential_name.split()) < 6:
                    is_section = True
                    break
            
            if is_section:
                continue
            
            # Add to found names (this will be in order)
            found_names.append(potential_name)
        
        # Pattern 2: Line contains "Scheme:" or "Name:"
        elif 'Scheme:' in line_clean or 'Name:' in line_clean:
            potential_name = line_clean.split(':', 1)[1].strip() if ':' in line_clean else line_clean
            
            # Skip if it's a section header
            is_skip = False
            for phrase in skip_phrases:
                if phrase.lower() in potential_name.lower():
                    is_skip = True
                    break
            
            if is_skip:
                continue
            
            if len(potential_name) > 5:
                found_names.append(potential_name)
        
        # Pattern 3: Line is a numbered list item with scheme name
        elif line_clean[0].isdigit() and '. ' in line_clean:
            potential_name = line_clean.split('. ', 1)[1].strip() if '. ' in line_clean else line_clean
            
            # Skip section headers
            is_skip = False
            for phrase in skip_phrases:
                if phrase.lower() in potential_name.lower():
                    is_skip = True
                    break
            
            if is_skip:
                continue
            
            if len(potential_name) > 5 and not potential_name.startswith('('):
                found_names.append(potential_name)
    
    # Return the LAST found scheme name (most recent)
    if found_names:
        return found_names[-1]
    
    return None

def chatbot_pipeline(query, history=None, session_id=None):
    history = history or []
    
    memory = get_conversation_memory(session_id or 'default_session')
    

    context_string = memory.build_context_string()
    
    # Check if this is a follow-up question
    follow_up_context = memory.get_follow_up_context(query)
    
    print(f"🔍 FOLLOW-UP DETECTION: {follow_up_context}")
    
    # ============================================================
    # HANDLE FOLLOW-UP QUESTIONS
    # ============================================================
    if follow_up_context.get('is_follow_up') and follow_up_context.get('needs_scheme_reference'):
        # If referenced_scheme is None, default to 1 (last scheme)
        if follow_up_context.get('referenced_scheme') is None:
            follow_up_context['referenced_scheme'] = 1
        
        scheme_name = ''
        referenced_scheme = None
        
        # ============================================================
        # FIX: For "it/that/this" references, use last_referenced_scheme
        # ============================================================
        is_pronoun_reference = (
            follow_up_context['referenced_scheme'] == 1 and 
            any(word in query.lower().split() for word in ['it', 'that', 'this', 'these', 'those'])
        )
        
        if is_pronoun_reference:
            # Try to get the last referenced scheme (the one user asked about)
            last_ref = memory.get_last_referenced_scheme()
            if last_ref:
                scheme_name = last_ref.get('name')
                referenced_scheme = last_ref.get('data')
                print(f"📌 Using last referenced scheme from context: {scheme_name}")
        
        # If not found, try from last_schemes
        if not scheme_name:
            last_schemes = memory.get_last_schemes()
            if last_schemes:
                scheme_index = follow_up_context['referenced_scheme'] - 1
                if scheme_index >= len(last_schemes) or scheme_index < 0:
                    print(f"⚠️ Scheme index {scheme_index} out of range, using first scheme")
                    scheme_index = 0
                
                referenced_scheme = last_schemes[scheme_index]
                
                if isinstance(referenced_scheme, dict):
                    scheme_name = referenced_scheme.get('scheme_name', '')
                    if not scheme_name:
                        scheme_name = referenced_scheme.get('name', '')
                else:
                    scheme_name = getattr(referenced_scheme, 'scheme_name', '')
                    if not scheme_name:
                        scheme_name = getattr(referenced_scheme, 'name', '')
        
        # If still not found, search history
        if not scheme_name:
            print(f"⚠️ Could not find scheme name, searching history...")
            for msg in reversed(memory.history):
                if msg['role'] == 'assistant':
                    content = msg['content']
                    extracted_name = extract_scheme_name_from_response(content)
                    if extracted_name:
                        scheme_name = extracted_name.replace('**', '').strip()
                        print(f"✅ Found scheme name from history: {scheme_name}")
                        break
        
        # If still no scheme_name, use fallback
        if not scheme_name:
            print(f"⚠️ Could not find scheme name, using fallback")
            scheme_name = "this scheme"
        
        # ============================================================
        # IMPORTANT: Store this as the last referenced scheme
        # ============================================================
        if scheme_name and scheme_name != "this scheme":
            memory.set_last_referenced_scheme(scheme_name, referenced_scheme)
            print(f"📌 Stored as last referenced scheme: {scheme_name}")
        
        # Determine what the user wants to know
        intent = follow_up_context.get('referenced_intent', 'SCHEME_SEARCH')
        
        # Build enhanced query
        if intent == 'APPLICATION':
            enhanced_query = f"How to apply for {scheme_name}"
        elif intent == 'ELIGIBILITY':
            enhanced_query = f"What is the eligibility for {scheme_name}"
        elif intent == 'BENEFITS':
            enhanced_query = f"What are the benefits of {scheme_name}"
        else:
            enhanced_query = f"Tell me about {scheme_name}"
        
        print(f"🔄 Follow-up: '{query}' → '{enhanced_query}'")
        query = enhanced_query
        
        # If we have referenced_scheme, use it; otherwise search
        if referenced_scheme:
            results = [{
                'score': 1.0,
                'scheme': referenced_scheme,
                'rerank_score': 1.0
            }]
        else:
            results = hybrid_search(query)
            if results:
                results = rerank_results(query, results)
        
        if not results:
            return {
                'success': False,
                'answer': "I couldn't find that scheme. Could you please specify which scheme you're asking about?",
                'schemes': [],
                'confidence': 0.0,
                'user_profile': {}
            }
        
        user_profile = profile_extractor.extract(query)
        
        # Generate follow-up response
        follow_up_answer = _build_follow_up_response(
            results, 
            query, 
            user_profile, 
            referenced_scheme=scheme_name,
            referenced_intent=intent
        )
        
        # Build response object
        response = {
            'success': True,
            'answer': clean_emoji(follow_up_answer),
            'confidence': 95.0,
            'intent': str(intent),
            'user_profile': user_profile,
            'follow_up': True,
            'referenced_scheme': scheme_name,
            'schemes': []
        }
        
        # Include scheme details
        for item in results[:5]:
            scheme = item['scheme']
            response['schemes'].append({
                'scheme_name': str(get_scheme_attr(scheme, 'scheme_name', '')),
                'details': str(get_scheme_attr(scheme, 'details', '')),
                'benefits': str(get_scheme_attr(scheme, 'benefits', '')),
                'eligibility': str(get_scheme_attr(scheme, 'eligibility', '')),
                'application': str(get_scheme_attr(scheme, 'application', '')),
                'documents': str(get_scheme_attr(scheme, 'documents', '')),
                'category': str(get_scheme_attr(scheme, 'schemeCategory', '')),
                'level': str(get_scheme_attr(scheme, 'level', '')),
                'score': 1.0,
                'profile_matches': item.get('profile_matches', [])
            })
        
        # Update memory
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