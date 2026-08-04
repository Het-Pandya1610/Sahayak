import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from chatbot.ai.classifier.intent_detector import detect_intent
from pathlib import Path
from llama_cpp import Llama # type: ignore
import random
import json
import os
import time

# ============================================================
# CONFIGURATION - SET TO FALSE TO DISABLE LLM (FAST)
# ============================================================
USE_LLM = False  # Set to True to enable LLM (SLOW)
LLM_TIMEOUT = 10.0  # Max seconds to wait for LLM

# ============================================================
# EMOJI HANDLING
# ============================================================
def clean_emoji(text):
    """Remove or replace emojis for console compatibility"""
    if not text:
        return text
    
    replacements = {
        '⚡': '[FAST]', '📋': '[INFO]', '📊': '[DATA]', '🎯': '[TARGET]',
        '✅': '[OK]', '⚠️': '[WARNING]', '📝': '[NOTE]', '🔍': '[SEARCH]',
        '🤖': '[AI]', '👋': '[WAVE]', '😊': ':)', '🚀': '[START]',
        '🎉': '[SUCCESS]', '💡': '[TIP]', '📚': '[BOOK]', '📖': '[READ]',
        '🏆': '[WIN]', '⭐': '[STAR]', '🔥': '[FIRE]', '💪': '[STRONG]',
        '🤝': '[HANDSHAKE]', '🙏': '[THANKS]', '💻': '[COMPUTER]',
        '📱': '[PHONE]', '🏠': '[HOME]', '💰': '[MONEY]', '🎓': '[GRADUATE]',
        '👨‍🎓': '[STUDENT]', '👩‍🎓': '[STUDENT]',
    }
    
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    
    import re
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text

# ============================================================
# Llama 3.1 8B Instruct Model Configuration - OPTIMIZED
# ============================================================
MODEL_PATH = "D:/Sahayak/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

if not os.path.exists(MODEL_PATH):
    print(f"WARNING: Llama 3.1 model not found at {MODEL_PATH}")
    MODEL_PATH = "D:/Sahayak/models/Qwen2.5.1-Coder-7B-Instruct-Q4_K_M.gguf"

# Only load LLM if USE_LLM is True (saves memory)
llm = None
if USE_LLM:
    print("Loading Llama 3.1 model...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,          # Reduced for speed
        n_threads=12,
        n_gpu_layers=35,
        offload_kqv=True,
        verbose=False
    )
    print("✅ Llama 3.1 loaded!")
else:
    print("⚡ LLM disabled - using template-only mode (FAST)")

# ============================================================
# Helper functions
# ============================================================
def get_scheme_attr(scheme, attr_name, default='N/A'):
    """Safely get attribute from either dict or MongoEngine object"""
    if scheme is None:
        return default
    if isinstance(scheme, dict):
        return scheme.get(attr_name, default)
    return getattr(scheme, attr_name, default)

def format_llama3_prompt(user_message, system_message=None):
    """Format prompt for Llama 3.1 Instruct model"""
    if system_message:
        return f"""<|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|>
<|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""
    else:
        return f"""<|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""

# ============================================================
# PROFILE-AWARE RESPONSE BUILDERS
# ============================================================
def _build_profile_summary(user_profile):
    """Build a summary of user profile for inclusion in responses"""
    if not user_profile or not any(user_profile.values()):
        return None
    
    profile_parts = []
    if user_profile.get('state'):
        profile_parts.append(f"State: {user_profile['state'].title()}")
    if user_profile.get('category'):
        profile_parts.append(f"Category: {user_profile['category'].upper()}")
    if user_profile.get('education'):
        edu_display = user_profile['education'].replace('_', ' ').title()
        profile_parts.append(f"Education: {edu_display}")
    if user_profile.get('gender'):
        profile_parts.append(f"Gender: {user_profile['gender'].title()}")
    if user_profile.get('income'):
        profile_parts.append(f"Income: ₹{int(user_profile['income']):,}")
    
    return ", ".join(profile_parts) if profile_parts else None

def _build_enhanced_schemes_text(results, max_schemes=5, user_profile=None):
    """Build enhanced scheme text with profile match indicators"""
    schemes_text = ""
    for i, item in enumerate(results[:max_schemes], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        profile_matches = item.get('profile_matches', [])
        boosted_score = item.get('boosted_score', score)
        
        scheme_name = get_scheme_attr(scheme, 'scheme_name', 'N/A')
        category = get_scheme_attr(scheme, 'schemeCategory', 'N/A')
        level = get_scheme_attr(scheme, 'level', 'N/A')
        details = get_scheme_attr(scheme, 'details', 'Not specified')
        benefits = get_scheme_attr(scheme, 'benefits', 'Not specified')
        eligibility = get_scheme_attr(scheme, 'eligibility', 'Not specified')
        application = get_scheme_attr(scheme, 'application', 'Not specified')
        documents = get_scheme_attr(scheme, 'documents', 'Not specified')
        
        # Add match indicators
        match_indicator = ""
        if profile_matches:
            match_indicator = f" [MATCHES: {', '.join(profile_matches).upper()}]"
        
        schemes_text += f"""
--- SCHEME {i} ---
NAME: {scheme_name}
CATEGORY: {category}
LEVEL: {level}
ABOUT: {details}
BENEFITS: {benefits}
ELIGIBILITY: {eligibility}
APPLICATION: {application}
DOCUMENTS: {documents}
RELEVANCE_SCORE: {boosted_score:.2f}
"""
    return schemes_text

# ============================================================
# LLM RESPONSE WITH PROFILE CONTEXT (Only if enabled)
# ============================================================
def _generate_llm_response_with_profile(query, intent, results, user_profile=None):
    """Generate response using Llama 3.1 with profile context (SLOW)"""
    
    if not USE_LLM or llm is None:
        return None
    
    schemes_text = _build_enhanced_schemes_text(results[:3], user_profile=user_profile)
    
    profile_summary = _build_profile_summary(user_profile)
    
    system_prompt = """You are Sahayak, a personalized government scheme assistant.

CRITICAL INSTRUCTIONS:
1. Use ONLY the database information provided below.
2. Personalize the response based on the user's profile.
3. DO NOT add external knowledge or information not in the database.
4. If information is not available, say "Information not available in the database."

Your response should:
- Address the user directly
- Highlight schemes that match their profile
- Provide clear next steps
- Be encouraging and helpful"""
    
    user_prompt = f"""User Query: {query}
Intent: {intent}
{profile_summary if profile_summary else "No profile information provided"}

DATABASE SCHEMES:
{schemes_text}

Provide a personalized, helpful response based on the user's query and profile:"""
    
    try:
        prompt = format_llama3_prompt(user_prompt, system_prompt)
        
        start = time.time()
        
        output = llm(
            prompt,
            max_tokens=200,        # Reduced from 300
            temperature=0.1,
            top_p=0.9,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            echo=False,
            repeat_penalty=1.1,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        elapsed = time.time() - start
        print(f"LLM generation took {elapsed:.2f}s")
        
        response = output['choices'][0]['text'].strip()
        
        if len(response) < 20:
            print("LLM response too short, using fallback")
            return None
            
        return clean_emoji(response)
        
    except Exception as e:
        print(f"LLM error: {e}")
        return None

# ============================================================
# GREETING RESPONSES
# ============================================================
GREETING_RESPONSES = {
    "GREETING": [
        "Hello! Welcome to Sahayak, your government scheme assistant. How can I help you today?",
        "Hi there! I'm here to help you find the right government scheme. What brings you here?",
        "Greetings! I can help you find scholarships, apply for schemes, and check eligibility. What would you like to know?"
    ],
    "THANKS": [
        "You're welcome! Happy to help. Is there anything else I can assist you with?",
        "My pleasure! Feel free to ask if you need more information about any scheme.",
        "Glad I could help! Let me know if you need more details about government schemes."
    ],
    "GOODBYE": [
        "Goodbye! Take care and good luck with your scheme application!",
        "Have a great day! Feel free to come back if you have more questions about government schemes.",
        "Bye! Wishing you success in finding the right scheme for your needs."
    ]
}

def get_greeting_response(intent):
    responses = GREETING_RESPONSES.get(intent, ["Hello! How can I help you?"])
    return random.choice(responses)

def llm_respond(intent, query):
    """Use Llama 3.1 for social intents (fast - small tokens)"""
    if intent in GREETING_RESPONSES:
        return get_greeting_response(intent)
    
    # If LLM is disabled, use template
    if not USE_LLM or llm is None:
        return "I'm here to help you with government schemes. What would you like to know?"
    
    try:
        system_prompt = "You are Sahayak, a helpful assistant for Indian government schemes. Provide brief, friendly responses."
        prompt = format_llama3_prompt(query, system_prompt)
        
        output = llm(
            prompt,
            max_tokens=80,
            temperature=0.7,
            stop=["<|eot_id|>", "\n\n\n"],
            echo=False
        )
        response = output['choices'][0]['text'].strip()
        if response:
            return clean_emoji(response)
    except Exception as e:
        print(f"LLM response error: {e}")
    
    return "I'm here to help you with government schemes. What would you like to know?"

# ============================================================
# FALLBACK RESPONSE BUILDERS (Profile-Aware) - CLEAN VERSION
# ============================================================
def _build_profile_aware_eligibility_response(results, query, user_profile=None):
    """Build eligibility response with profile context"""
    schemes = []
    profile_summary = _build_profile_summary(user_profile)
    
    for i, item in enumerate(results[:5], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        profile_matches = item.get('profile_matches', [])
        
        scheme_name = get_scheme_attr(scheme, 'scheme_name', 'N/A')
        category = get_scheme_attr(scheme, 'schemeCategory', 'N/A')
        level = get_scheme_attr(scheme, 'level', 'N/A')
        eligibility = get_scheme_attr(scheme, 'eligibility', 'Not specified')
        
        match_indicator = ""
        if profile_matches:
            match_indicator = f" [MATCHES: {', '.join(profile_matches).upper()}]"
        
        schemes.append(f"""
{i}. {scheme_name}
   - Category: {category} | Level: {level}
   - Eligibility: {eligibility}
""")
    
    profile_intro = ""
    if profile_summary:
        profile_intro = f"Based on your profile, here are the most relevant schemes:\n\n"
    else:
        profile_intro = "Based on your query, here are the most relevant schemes:\n\n"
    
    return clean_emoji(f"""{profile_intro}{chr(10).join(schemes)}

Next Steps:
1. Review the eligibility criteria carefully
2. Check if you meet all requirements
3. Prepare the required documents
4. Apply through the official portal

Would you like more details about any specific scheme?
""")

def _build_profile_aware_recommendation_response(results, query, user_profile=None):
    """Build recommendation response with profile context"""
    schemes = []
    profile_summary = _build_profile_summary(user_profile)
    
    for i, item in enumerate(results[:5], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        profile_matches = item.get('profile_matches', [])
        
        scheme_name = get_scheme_attr(scheme, 'scheme_name', 'N/A')
        category = get_scheme_attr(scheme, 'schemeCategory', 'N/A')
        benefits = get_scheme_attr(scheme, 'benefits', 'Not specified')
        eligibility = get_scheme_attr(scheme, 'eligibility', 'Not specified')
        
        match_indicator = ""
        if profile_matches:
            match_indicator = f" [MATCHES: {', '.join(profile_matches).upper()}]"
        
        schemes.append(f"""
{i}. {scheme_name}
   - Category: {category}
   - Key Benefits: {benefits if benefits else 'Not specified'}
   - Eligibility: {eligibility if eligibility else 'Not specified'}
""")
    
    profile_intro = ""
    if profile_summary:
        profile_intro = f"Based on your profile ({profile_summary}), I recommend these schemes:\n\n"
    else:
        profile_intro = "Based on your query, here are the top recommended schemes:\n\n"
    
    return clean_emoji(f"""{profile_intro}{chr(10).join(schemes)}

To apply for these schemes:
1. Visit the official government portal
2. Check detailed eligibility requirements
3. Gather required documents
4. Submit your application online

Which scheme would you like more information about?
""")

def _build_scheme_details_response(results, query, user_profile=None):
    """Build detailed scheme information response"""
    top = results[0]['scheme']
    profile_matches = results[0].get('profile_matches', [])
    
    scheme_name = get_scheme_attr(top, 'scheme_name', 'N/A')
    details = get_scheme_attr(top, 'details', 'Not specified')
    benefits = get_scheme_attr(top, 'benefits', 'Not specified')
    eligibility = get_scheme_attr(top, 'eligibility', 'Not specified')
    application = get_scheme_attr(top, 'application', 'Not specified')
    documents = get_scheme_attr(top, 'documents', 'Not specified')
    category = get_scheme_attr(top, 'schemeCategory', 'N/A')
    level = get_scheme_attr(top, 'level', 'N/A')
    
    match_indicator = ""
    if profile_matches:
        match_indicator = f" [This scheme matches your {', '.join(profile_matches)}]"
    
    return clean_emoji(f"""
[INFO] {scheme_name}

About the Scheme:
{details}

Benefits:
{benefits}

Eligibility Criteria:
{eligibility}

Application Process:
{application}

Required Documents:
{documents}

Category: {category}
Level: {level}

Would you like more details about any specific aspect of this scheme?
""")

def _build_general_response(results, query, user_profile=None):
    """Build general response with profile context"""
    top = results[0]['scheme']
    profile_matches = results[0].get('profile_matches', [])
    
    scheme_name = get_scheme_attr(top, 'scheme_name', 'N/A')
    details = get_scheme_attr(top, 'details', 'Not specified')
    benefits = get_scheme_attr(top, 'benefits', 'Not specified')
    category = get_scheme_attr(top, 'schemeCategory', 'N/A')
    level = get_scheme_attr(top, 'level', 'N/A')
    
    match_indicator = ""
    if profile_matches:
        match_indicator = f" (Matches your {', '.join(profile_matches)})"
    
    return clean_emoji(f"""
{scheme_name}

About:
{details}

Benefits:
{benefits}

Category: {category} | Level: {level}

Would you like more details about eligibility or application process?
""")

# ============================================================
# MAIN GENERATE FUNCTION - PROFILE AWARE (FAST)
# ============================================================
def generate_response(query, results, history=None, user_profile=None):
    """Enhanced response generation with profile awareness - FAST MODE"""
    
    if history is None:
        history = []

    if user_profile is None:
        user_profile = {}

    intent = detect_intent(query)
    
    print("=" * 50)
    print(f"QUERY: {query}")
    print(f"INTENT: {intent}")
    print(f"RESULTS: {len(results) if results else 0}")
    print(f"PROFILE: {user_profile}")
    print(f"LLM: {'ENABLED' if USE_LLM else 'DISABLED (FAST)'}")
    print("=" * 50)

    # Handle social intents instantly
    if intent in ["GREETING", "THANKS", "GOODBYE"]:
        return {
            'success': True,
            'answer': llm_respond(intent, query),
            'schemes': []
        }

    if not results:
        return {
            'success': False,
            'answer': "I couldn't find any specific government schemes matching your query. Could you please provide more details?",
            'schemes': []
        }

    # ============================================================
    # FAST PATH: Use profile-aware templates (ALWAYS)
    # ============================================================
    query_lower = query.lower()
    
    # Check for template matches
    if "eligibility" in query_lower or "eligible" in query_lower:
        print("⚡ Using eligibility template")
        response_text = _build_profile_aware_eligibility_response(results, query, user_profile)
    elif "benefit" in query_lower or "benefits" in query_lower:
        print("⚡ Using benefits template")
        response_text = _build_profile_aware_recommendation_response(results, query, user_profile)
    elif "apply" in query_lower or "application" in query_lower:
        print("⚡ Using application template")
        response_text = _build_scheme_details_response(results, query, user_profile)
    elif "document" in query_lower or "documents" in query_lower:
        print("⚡ Using documents template")
        response_text = _build_scheme_details_response(results, query, user_profile)
    elif "recommend" in query_lower or "suggest" in query_lower or "best" in query_lower:
        print("⚡ Using recommendation template")
        response_text = _build_profile_aware_recommendation_response(results, query, user_profile)
    else:
        # Use appropriate template based on intent
        if intent in ["SCHEME_SEARCH", "ELIGIBILITY"]:
            response_text = _build_profile_aware_eligibility_response(results, query, user_profile)
        elif intent in ["RECOMMENDATION"]:
            response_text = _build_profile_aware_recommendation_response(results, query, user_profile)
        else:
            response_text = _build_general_response(results, query, user_profile)
    
    # ============================================================
    # OPTIONAL: Try LLM if enabled (but don't wait too long)
    # ============================================================
    if USE_LLM and llm is not None:
        print("🔄 Starting LLM generation in background (max 10s)...")
        start_time = time.time()
        llm_response = _generate_llm_response_with_profile(query, intent, results, user_profile)
        elapsed = time.time() - start_time
        
        if llm_response is not None:
            print(f"✅ LLM completed in {elapsed:.1f}s, using LLM response")
            response_text = llm_response
        else:
            print(f"⚡ LLM failed/timed out, using template response")

    # Build final response
    confidence = float(min(round(results[0].get('boosted_score', results[0].get('rerank_score', results[0].get('score', 0))) * 100, 2), 99.0))
    
    response = {
        'success': True,
        'answer': clean_emoji(response_text),
        'confidence': confidence,
        'intent': str(intent),
        'user_profile': user_profile,
        'schemes': []
    }

    # Include scheme details with profile match info
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
            'score': float(round(item.get('boosted_score', item.get('rerank_score', item.get('score', 0))), 3)),
            'profile_matches': item.get('profile_matches', [])
        })

    return response