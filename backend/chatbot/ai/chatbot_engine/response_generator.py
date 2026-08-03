from chatbot.ai.classifier.intent_detector import detect_intent
from pathlib import Path
from llama_cpp import Llama # type: ignore
import random
import json

MODEL_PATH = "D:/Sahayak/models/Qwen2.5.1-Coder-7B-Instruct-Q4_K_M.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=32768,
    n_threads=8,
    verbose=False
)

GREETING_RESPONSES = {
    "GREETING": [
        "Hello! 👋 Welcome to Sahayak, your government scheme assistant. How can I help you today?",
        "Hi there! I'm here to help you find the right government scheme. What brings you here?",
        "Greetings! I can help you find scholarships, apply for schemes, and check eligibility. What would you like to know?"
    ],
    "THANKS": [
        "You're welcome! 😊 Happy to help. Is there anything else I can assist you with?",
        "My pleasure! Feel free to ask if you need more information about any scheme.",
        "Glad I could help! Let me know if you need more details about government schemes."
    ],
    "GOODBYE": [
        "Goodbye! 👋 Take care and good luck with your scheme application!",
        "Have a great day! Feel free to come back if you have more questions about government schemes.",
        "Bye! Wishing you success in finding the right scheme for your needs."
    ]
}

def get_greeting_response(intent):
    responses = GREETING_RESPONSES.get(intent, ["Hello! How can I help you?"])
    return random.choice(responses)

def llm_respond(intent, query):
    """Fallback LLM response for social intents."""
    if intent in GREETING_RESPONSES:
        return get_greeting_response(intent)
    
    prompts = {
        "GREETING": "User says: 'Hello'. Respond as a helpful assistant for government schemes.",
        "THANKS": "User says: 'Thank you'. Respond politely and offer further help.",
        "GOODBYE": "User says: 'Goodbye'. Respond with a warm farewell."
    }
    prompt = prompts.get(intent, f"User says: '{query}'. Respond briefly and helpfully.")
    output = llm(f"<|user|>\n{prompt}\n<|assistant|>\n", max_tokens=60, stop=["<|end|>", "\n\n"])
    return output['choices'][0]['text'].strip()

def _build_scheme_list(results, max_schemes=5):
    """Build formatted scheme list with proper float conversion."""
    schemes = []
    for i, item in enumerate(results[:max_schemes], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        schemes.append(f"""
{i}. **{scheme.get('scheme_name', 'N/A')}** (Relevance: {score:.2f})
   - Category: {scheme.get('schemeCategory', 'N/A')}
   - Level: {scheme.get('level', 'N/A')}
""")
    return "\n".join(schemes)

def _build_scheme_details_response(results, query):
    """Build detailed scheme information response with all fields."""
    top = results[0]['scheme']
    
    # Build comprehensive response with all available information
    response = f"""
**{top.get('scheme_name', 'N/A')}** - Complete Details

**About the Scheme:**
{top.get('details', 'Not specified')}

**Benefits:**
{top.get('benefits', 'Not specified')}

**Eligibility Criteria:**
{top.get('eligibility', 'Not specified')}

**Application Process:**
{top.get('application', 'Not specified')}

**Required Documents:**
{top.get('documents', 'Not specified')}

**Category:** {top.get('schemeCategory', 'N/A')}
**Level:** {top.get('level', 'N/A')}

Would you like more details about any specific aspect of this scheme?
"""
    return response

def _build_eligibility_response(results, query):
    """Build detailed eligibility response."""
    schemes = []
    for item in results[:3]:
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        schemes.append(f"""
**{scheme.get('scheme_name', 'N/A')}** (Relevance: {score:.2f})
- Eligibility: {scheme.get('eligibility', 'Not specified')}
- Category: {scheme.get('schemeCategory', 'N/A')}
- Level: {scheme.get('level', 'N/A')}
""")
    
    return f"""Based on your eligibility query, here are the most relevant schemes:

{chr(10).join(schemes)}

**Next Steps:**
1. Review the eligibility criteria carefully
2. Check if you meet all the requirements
3. Prepare the required documents
4. Apply through the official portal

Would you like more details about any specific scheme?"""

def _build_recommendation_response(results, query):
    """Build comprehensive recommendation response."""
    schemes = []
    for i, item in enumerate(results[:5], 1):
        scheme = item['scheme']
        score = float(item.get('rerank_score', item.get('score', 0)))
        schemes.append(f"""
{i}. **{scheme.get('scheme_name', 'N/A')}**
   - Category: {scheme.get('schemeCategory', 'N/A')}
   - Key Benefit: {scheme.get('benefits', 'Not specified')[:100]}...
   - Eligibility: {scheme.get('eligibility', 'Not specified')[:80]}...
""")
    
    return f"""Based on your query, here are the top recommended schemes:

{chr(10).join(schemes)}

**To apply for these schemes:**
1. Visit the official government portal
2. Check detailed eligibility requirements
3. Gather required documents
4. Submit your application online

Which scheme would you like more information about?"""

def _build_application_response(results, query):
    """Build detailed application response."""
    top = results[0]['scheme']
    return f"""
**Application Process for {top.get('scheme_name', 'N/A')}**

**Step-by-Step Guide:**
{top.get('application', 'Not specified')}

**Required Documents:**
{top.get('documents', 'Not specified')}

**Important Tips:**
- Apply before the deadline
- Keep all documents ready in digital format
- Double-check all information before submission
- Save your application reference number

Need help with document preparation?"""

def _build_documents_response(results, query):
    """Build documents response."""
    top = results[0]['scheme']
    return f"""
**Required Documents for {top.get('scheme_name', 'N/A')}**

{top.get('documents', 'Not specified')}

**Additional Tips:**
- Make sure all documents are valid and current
- Self-attest all copies before submission
- Keep originals ready for verification
- Scan documents as per the specified format

Would you like to know the application process as well?"""

def _build_benefits_response(results, query):
    """Build benefits response."""
    top = results[0]['scheme']
    return f"""
**Benefits of {top.get('scheme_name', 'N/A')}**

{top.get('benefits', 'Not specified')}

**Eligibility at a Glance:**
{top.get('eligibility', 'Not specified')}

**How to Access:**
{top.get('application', 'Not specified')}

Any specific aspect you'd like me to elaborate on?"""

def _build_general_response(results, query):
    """Build general scheme information response."""
    top = results[0]['scheme']
    return f"""
**{top.get('scheme_name', 'N/A')}** - Key Information

**About:**
{top.get('details', 'Not specified')}

**Benefits:**
{top.get('benefits', 'Not specified')}

**Eligibility:**
{top.get('eligibility', 'Not specified')}

**Application Process:**
{top.get('application', 'Not specified')}

**Required Documents:**
{top.get('documents', 'Not specified')}

Would you like more details about any specific aspect?
"""

def generate_response(query, results, history=None):
    """Enhanced response generation with proper JSON serialization."""
    
    if history is None:
        history = []

    intent = detect_intent(query)
    
    print("=" * 50)
    print(f"QUERY: {query}")
    print(f"INTENT: {intent}")
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
            'answer': "I couldn't find any specific government schemes matching your query. Could you please provide more details?",
            'schemes': []
        }

    # Ensure scores are Python floats
    for item in results:
        if 'rerank_score' in item:
            item['rerank_score'] = float(item['rerank_score'])
        if 'score' in item:
            item['score'] = float(item['score'])

    top_scheme = results[0]['scheme']
    confidence = float(min(round(results[0].get('rerank_score', results[0].get('score', 0)) * 100, 2), 99.0))

    # Build comprehensive response based on intent
    if intent == "ELIGIBILITY":
        response_text = _build_eligibility_response(results, query)
    elif intent == "RECOMMENDATION":
        response_text = _build_recommendation_response(results, query)
    elif intent == "APPLICATION":
        response_text = _build_application_response(results, query)
    elif intent == "DOCUMENTS":
        response_text = _build_documents_response(results, query)
    elif intent == "BENEFITS":
        response_text = _build_benefits_response(results, query)
    elif intent == "SCHEME_SEARCH":
        # Use detailed scheme response for scheme search queries
        response_text = _build_scheme_details_response(results, query)
    else:
        response_text = _build_general_response(results, query)

    # Build final response with proper Python types
    response = {
        'success': True,
        'answer': response_text,
        'confidence': float(confidence),
        'intent': str(intent),
        'schemes': []
    }

    # Include scheme details with proper float conversion
    for item in results[:5]:
        scheme = item['scheme']
        response['schemes'].append({
            'scheme_name': str(scheme.get('scheme_name', '')),
            'details': str(scheme.get('details', '')),
            'benefits': str(scheme.get('benefits', '')),
            'eligibility': str(scheme.get('eligibility', '')),
            'application': str(scheme.get('application', '')),
            'documents': str(scheme.get('documents', '')),
            'category': str(scheme.get('schemeCategory', '')),
            'level': str(scheme.get('level', '')),
            'score': float(round(item.get('rerank_score', item.get('score', 0)), 3))
        })

    return response