import sys
import io
import re
import random
import os
import time
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from chatbot.ai.classifier.intent_detector import detect_intent
from llama_cpp import Llama

# ============================================================
# CONFIGURATION
# ============================================================
USE_LLM = False
LLM_TIMEOUT = 10.0

# ============================================================
# EMOJI HANDLING
# ============================================================
def clean_emoji(text):
    """Clean emojis for console compatibility"""
    if not text:
        return text
    
    replacements = {
        '⚡': '⚡', '📋': '📋', '📊': '📊', '🎯': '🎯',
        '✅': '✅', '⚠️': '⚠️', '📝': '📝', '🔍': '🔍',
        '🤖': '🤖', '👋': '👋', '😊': '😊', '🚀': '🚀',
        '🎉': '🎉', '💡': '💡', '📚': '📚', '📖': '📖',
        '🏆': '🏆', '⭐': '⭐', '🔥': '🔥', '💪': '💪',
        '🤝': '🤝', '🙏': '🙏', '💻': '💻', '📱': '📱',
        '🏠': '🏠', '💰': '💰', '🎓': '🎓',
        '👨‍🎓': '👨‍🎓', '👩‍🎓': '👩‍🎓',
    }
    
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    
    return text

def get_scheme_attr(scheme, attr_name, default='N/A'):
    """Safely get attribute from either dict or MongoEngine object"""
    if scheme is None:
        return default
    if isinstance(scheme, dict):
        return scheme.get(attr_name, default)
    return getattr(scheme, attr_name, default)

# ============================================================
# LLAMA MODEL CONFIGURATION
# ============================================================
MODEL_PATH = "D:/Sahayak/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

if not os.path.exists(MODEL_PATH):
    print(f"⚠️ Model not found at {MODEL_PATH}")
    MODEL_PATH = "D:/Sahayak/models/Qwen2.5.1-Coder-7B-Instruct-Q4_K_M.gguf"

llm = None
if USE_LLM:
    print("🤖 Loading Llama 3.1 model...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=12,
        n_gpu_layers=35,
        offload_kqv=True,
        verbose=False
    )
    print("✅ Llama 3.1 loaded!")
else:
    print("⚡ LLM disabled - using template-only mode")

# ============================================================
# FORMAT FUNCTIONS
# ============================================================
def format_llama3_prompt(user_message, system_message=None):
    """Format prompt for Llama 3.1"""
    if system_message:
        return f"""<|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|>
<|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""
    return f"""<|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""

# ============================================================
# PROFILE SUMMARY
# ============================================================
def _build_profile_summary(user_profile):
    """Build user profile summary"""
    if not user_profile or not any(user_profile.values()):
        return None
    
    parts = []
    if user_profile.get('state'):
        parts.append(f"📍 State: {user_profile['state'].title()}")
    if user_profile.get('category'):
        parts.append(f"📋 Category: {user_profile['category'].upper()}")
    if user_profile.get('education'):
        parts.append(f"🎓 Education: {user_profile['education'].replace('_', ' ').title()}")
    if user_profile.get('gender'):
        parts.append(f"👤 Gender: {user_profile['gender'].title()}")
    if user_profile.get('income'):
        parts.append(f"💰 Income: ₹{int(user_profile['income']):,}")
    
    return " | ".join(parts) if parts else None

# ============================================================
# BEAUTIFIED RESPONSE BUILDERS
# ============================================================

def _format_section(title, content, icon="📌"):
    """Format a section with title and content"""
    if not content or content == 'Not specified':
        return ""
    return f"\n{icon} **{title}**\n{content}\n"

def _format_list(items, bullet="•"):
    """Format a list of items with bullets"""
    if not items:
        return ""
    return "\n".join([f"  {bullet} {item}" for item in items])

def _format_step(step):
    """Format a step with number"""
    return f"  {step}"

def _build_beautiful_response(
    scheme_name, 
    details=None, 
    benefits=None, 
    eligibility=None, 
    application=None, 
    documents=None,
    category=None,
    level=None,
    profile_matches=None,
    intent=None,
    query=None
):
    """Build a beautiful, conversational response like a human assistant"""
    
    # Greeting based on context
    greeting = "Here's what I found for you" if scheme_name else "I found some relevant schemes"
    
    # Build response parts
    parts = []
    
    # ============================================================
    # HEADER with emojis
    # ============================================================
    if scheme_name and scheme_name != 'N/A':
        parts.append(f"\n🌟 **{scheme_name}**")
        if category and category != 'N/A':
            parts.append(f"📂 *{category}*")
    
    # ============================================================
    # PROFILE MATCHES
    # ============================================================
    if profile_matches:
        parts.append(f"\n🎯 This scheme matches your {', '.join(profile_matches)}!")
    
    # ============================================================
    # ABOUT / DETAILS
    # ============================================================
    if details and details != 'Not specified':
        parts.append(f"\n📌 **About**\n{details}")
    
    # ============================================================
    # BENEFITS
    # ============================================================
    if benefits and benefits != 'Not specified':
        # Try to format benefits as bullet points
        if '\n' in benefits or '•' in benefits:
            parts.append(f"\n✨ **Benefits**\n{benefits}")
        else:
            parts.append(f"\n✨ **Benefits**\n{benefits}")
    
    # ============================================================
    # ELIGIBILITY
    # ============================================================
    if eligibility and eligibility != 'Not specified':
        parts.append(f"\n✅ **Eligibility Criteria**\n{eligibility}")
    
    # ============================================================
    # APPLICATION PROCESS
    # ============================================================
    if application and application != 'Not specified':
        parts.append(f"\n📝 **How to Apply**\n{application}")
    
    # ============================================================
    # DOCUMENTS
    # ============================================================
    if documents and documents != 'Not specified':
        parts.append(f"\n📄 **Required Documents**\n{documents}")
    
    # ============================================================
    # METADATA
    # ============================================================
    meta_parts = []
    if category and category != 'N/A':
        meta_parts.append(f"📂 {category}")
    if level and level != 'N/A':
        meta_parts.append(f"🌍 {level}")
    
    if meta_parts:
        parts.append(f"\n📊 **Details**\n" + "\n".join(f"  • {m}" for m in meta_parts))
    
    # ============================================================
    # FOLLOW-UP SUGGESTION
    # ============================================================
    parts.append(f"\n💡 **Need more help?**")
    
    # Intent-based follow-up suggestions
    suggestions = []
    if intent == 'ELIGIBILITY':
        suggestions.append("Check if you meet all requirements")
        suggestions.append("Ask about application process")
    elif intent == 'BENEFITS':
        suggestions.append("Ask about eligibility criteria")
        suggestions.append("Learn about application process")
    elif intent == 'APPLICATION':
        suggestions.append("Ask about eligibility")
        suggestions.append("Learn about required documents")
    else:
        suggestions.append("Ask about eligibility criteria")
        suggestions.append("Learn about benefits")
        suggestions.append("Get application guidance")
    
    parts.append("You can ask me:\n" + "\n".join(f"  • {s}" for s in suggestions[:3]))
    
    parts.append("\n🤝 *I'm here to help!*")
    
    return "\n".join(parts)

# ============================================================
# RESPONSE BUILDERS (Updated with beautiful formatting)
# ============================================================

def _build_profile_aware_eligibility_response(results, query, user_profile=None):
    """Build beautiful eligibility response"""
    schemes = []
    profile_summary = _build_profile_summary(user_profile)
    
    for i, item in enumerate(results[:5], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        
        scheme_name = get_scheme_attr(scheme, 'scheme_name', 'N/A')
        category = get_scheme_attr(scheme, 'schemeCategory', 'N/A')
        level = get_scheme_attr(scheme, 'level', 'N/A')
        eligibility = get_scheme_attr(scheme, 'eligibility', 'Not specified')
        
        schemes.append(f"""
**{i}. {scheme_name}** ({score*100:.0f}% match)
   📂 {category} | 🌍 {level}
   ✅ {eligibility[:150]}...
""")
    
    intro = "🎯 **Based on your profile**, here are the most relevant schemes:" if profile_summary else "📋 **Based on your query**, here are the most relevant schemes:"
    
    return clean_emoji(f"""
{intro}

{chr(10).join(schemes)}

---
**📌 Next Steps:**
1️⃣ Review the eligibility criteria carefully
2️⃣ Check if you meet all requirements
3️⃣ Prepare the required documents
4️⃣ Apply through the official portal

💡 Would you like more details about any specific scheme?
""")

def _build_profile_aware_recommendation_response(results, query, user_profile=None):
    """Build beautiful recommendation response"""
    schemes = []
    profile_summary = _build_profile_summary(user_profile)
    
    for i, item in enumerate(results[:5], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        
        scheme_name = get_scheme_attr(scheme, 'scheme_name', 'N/A')
        category = get_scheme_attr(scheme, 'schemeCategory', 'N/A')
        benefits = get_scheme_attr(scheme, 'benefits', 'Not specified')
        eligibility = get_scheme_attr(scheme, 'eligibility', 'Not specified')
        
        schemes.append(f"""
**{i}. {scheme_name}** ({score*100:.0f}% match)
   📂 {category}
   💰 {benefits[:100]}...
   ✅ {eligibility[:80]}...
""")
    
    intro = f"🎯 **Based on your profile** ({profile_summary}), I recommend these schemes:" if profile_summary else "📋 **Based on your query**, here are the top recommended schemes:"
    
    return clean_emoji(f"""
{intro}

{chr(10).join(schemes)}

---
**📌 To apply for these schemes:**
1️⃣ Visit the official government portal
2️⃣ Check detailed eligibility requirements
3️⃣ Gather required documents
4️⃣ Submit your application online

💡 Which scheme would you like more information about?
""")

def _build_scheme_details_response(results, query, user_profile=None):
    """Build beautiful detailed scheme response"""
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
    
    return _build_beautiful_response(
        scheme_name=scheme_name,
        details=details,
        benefits=benefits,
        eligibility=eligibility,
        application=application,
        documents=documents,
        category=category,
        level=level,
        profile_matches=profile_matches
    )

def _build_general_response(results, query, user_profile=None):
    """Build beautiful general response"""
    top = results[0]['scheme']
    profile_matches = results[0].get('profile_matches', [])
    
    scheme_name = get_scheme_attr(top, 'scheme_name', 'N/A')
    details = get_scheme_attr(top, 'details', 'Not specified')
    benefits = get_scheme_attr(top, 'benefits', 'Not specified')
    category = get_scheme_attr(top, 'schemeCategory', 'N/A')
    level = get_scheme_attr(top, 'level', 'N/A')
    
    return _build_beautiful_response(
        scheme_name=scheme_name,
        details=details,
        benefits=benefits,
        category=category,
        level=level,
        profile_matches=profile_matches
    )

def _build_follow_up_response(results, query, user_profile=None, referenced_scheme=None, referenced_intent=None):
    """Build beautiful follow-up response"""
    if not results:
        return "I couldn't find that scheme. Could you please specify which scheme you're asking about?"
    
    top = results[0]['scheme']
    
    scheme_name = get_scheme_attr(top, 'scheme_name', 'N/A')
    details = get_scheme_attr(top, 'details', 'Not specified')
    benefits = get_scheme_attr(top, 'benefits', 'Not specified')
    eligibility = get_scheme_attr(top, 'eligibility', 'Not specified')
    application = get_scheme_attr(top, 'application', 'Not specified')
    documents = get_scheme_attr(top, 'documents', 'Not specified')
    category = get_scheme_attr(top, 'schemeCategory', 'N/A')
    level = get_scheme_attr(top, 'level', 'N/A')
    
    intent = referenced_intent or ''
    query_lower = query.lower()
    
    # Build response based on intent
    if intent == 'APPLICATION' or "apply" in query_lower or "application" in query_lower or "process" in query_lower:
        return clean_emoji(f"""
📝 **Application Process for {scheme_name}**

---
**Step-by-Step Guide:**
{application if application else 'ℹ️ Information not available in the database.'}

**📄 Required Documents:**
{documents if documents else 'ℹ️ Information not available in the database.'}

---
**💡 Important Tips:**
• Apply before the deadline
• Keep all documents ready in digital format
• Double-check all information before submission
• Save your application reference number

🔍 Need more help with the application process?
""")
    
    elif intent == 'ELIGIBILITY' or "eligibility" in query_lower or "eligible" in query_lower or "qualify" in query_lower:
        return clean_emoji(f"""
✅ **Eligibility Criteria for {scheme_name}**

---
{eligibility if eligibility else 'ℹ️ Information not available in the database.'}

**📊 Additional Details:**
• Category: {category}
• Level: {level}

---
🔍 Check if you meet all requirements before applying.
💡 Would you like to know about the application process?
""")
    
    elif intent == 'BENEFITS' or "benefit" in query_lower or "benefits" in query_lower or "amount" in query_lower:
        return clean_emoji(f"""
💰 **Benefits of {scheme_name}**

---
{benefits if benefits else 'ℹ️ Information not available in the database.'}

**📋 Eligibility at a Glance:**
{eligibility if eligibility else 'ℹ️ Information not available in the database.'}

---
💡 Any specific aspect you'd like me to elaborate on?
""")

    elif intent == 'DOCUMENTS' or "document" in query_lower or "documents" in query_lower or "paperwork" in query_lower:
        return clean_emoji(f"""
📄 **Required Documents for {scheme_name}**

---
{documents if documents else 'ℹ️ Information not available in the database.'}

**📝 Application Process:**
{application if application else 'ℹ️ Information not available in the database.'}

---
💡 Let me know if you want to know about eligibility or benefits for this scheme.
""")
    
    else:
        # General details
        return clean_emoji(f"""
🌟 **{scheme_name}**

---
**📌 About:**
{details}

**💰 Benefits:**
{benefits}

**✅ Eligibility:**
{eligibility}

**📝 Application Process:**
{application}

**📄 Required Documents:**
{documents}

**📊 Details:**
• Category: {category}
• Level: {level}

---
💡 Would you like more details about any specific aspect?
""")

# ============================================================
# GREETING RESPONSES
# ============================================================
GREETING_RESPONSES = {
    "GREETING": [
        "👋 Hello! Welcome to **Sahayak**, your government scheme assistant. How can I help you today?",
        "🌟 Hi there! I'm here to help you find the right government scheme. What brings you here?",
        "🙏 Greetings! I can help you find scholarships, apply for schemes, and check eligibility. What would you like to know?"
    ],
    "THANKS": [
        "😊 You're welcome! Happy to help. Is there anything else I can assist you with?",
        "🙏 My pleasure! Feel free to ask if you need more information about any scheme.",
        "🤝 Glad I could help! Let me know if you need more details about government schemes."
    ],
    "GOODBYE": [
        "👋 Goodbye! Take care and good luck with your scheme application!",
        "🌟 Have a great day! Feel free to come back if you have more questions.",
        "🙏 Bye! Wishing you success in finding the right scheme for your needs."
    ]
}

def get_greeting_response(intent):
    responses = GREETING_RESPONSES.get(intent, ["Hello! How can I help you?"])
    return random.choice(responses)

def llm_respond(intent, query):
    """Use Llama 3.1 for social intents"""
    if intent in GREETING_RESPONSES:
        return get_greeting_response(intent)
    
    if not USE_LLM or llm is None:
        return "💡 I'm here to help you with government schemes. What would you like to know?"
    
    try:
        system_prompt = "You are Sahayak, a helpful assistant for Indian government schemes."
        prompt = format_llama3_prompt(query, system_prompt)
        output = llm(prompt, max_tokens=80, temperature=0.7, stop=["<|eot_id|>", "\n\n\n"], echo=False)
        response = output['choices'][0]['text'].strip()
        return clean_emoji(response) if response else "💡 I'm here to help you with government schemes. What would you like to know?"
    except Exception as e:
        print(f"LLM response error: {e}")
    
    return "💡 I'm here to help you with government schemes. What would you like to know?"

# ============================================================
# MAIN GENERATE FUNCTION
# ============================================================
def generate_response(query, results, history=None, user_profile=None):
    """Enhanced response generation with beautiful formatting"""
    
    if history is None:
        history = []

    if user_profile is None:
        user_profile = {}

    intent = detect_intent(query)
    
    print("=" * 50)
    print(f"📝 QUERY: {query}")
    print(f"🎯 INTENT: {intent}")
    print(f"📊 RESULTS: {len(results) if results else 0}")
    print(f"👤 PROFILE: {user_profile}")
    print(f"🤖 LLM: {'ENABLED' if USE_LLM else 'DISABLED'}")
    print("=" * 50)

    # Handle social intents
    if intent in ["GREETING", "THANKS", "GOODBYE"]:
        return {
            'success': True,
            'answer': llm_respond(intent, query),
            'schemes': []
        }

    if not results:
        return {
            'success': False,
            'answer': "🔍 I couldn't find any specific government schemes matching your query. Could you please provide more details?",
            'schemes': []
        }

    # Use profile-aware templates
    query_lower = query.lower()
    
    # Choose template based on query
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
        if intent in ["SCHEME_SEARCH", "ELIGIBILITY"]:
            response_text = _build_profile_aware_eligibility_response(results, query, user_profile)
        elif intent in ["RECOMMENDATION"]:
            response_text = _build_profile_aware_recommendation_response(results, query, user_profile)
        else:
            response_text = _build_general_response(results, query, user_profile)
    
    # Try LLM if enabled
    if USE_LLM and llm is not None:
        print("🔄 Starting LLM generation...")
        start_time = time.time()
        llm_response = _generate_llm_response_with_profile(query, intent, results, user_profile)
        elapsed = time.time() - start_time
        
        if llm_response is not None:
            print(f"✅ LLM completed in {elapsed:.1f}s")
            response_text = llm_response
        else:
            print("⚡ LLM failed, using template")

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
            'score': float(round(item.get('boosted_score', item.get('rerank_score', item.get('score', 0))), 3)),
            'profile_matches': item.get('profile_matches', [])
        })

    return response