from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import numpy as np # type: ignore
import re

# Load once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

INTENT_EXAMPLES = {
    "GREETING": [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "namaste", "greetings", "morning", "evening"
    ],
    "THANKS": [
        "thanks", "thank you", "thanks a lot", "thx", "appreciate it",
        "thank you so much", "very helpful", "great help"
    ],
    "GOODBYE": [
        "bye", "goodbye", "see you", "take care", "have a good day",
        "bye bye", "see you later"
    ],
    "FOLLOWUP": [
        "what about", "tell me more", "more details", "can you explain further",
        "also", "additionally", "and", "what else", "could you elaborate"
    ],
    "ELIGIBILITY": [
        "am i eligible", "can i apply", "can i get this scheme", 
        "what schemes am i eligible for", "eligibility criteria",
        "do i qualify", "i am a student what schemes can i get",
        "i belong to sc category what schemes can i get",
        "who can apply", "qualification required", "conditions to apply",
        "eligibility requirements", "am I qualified for",
        "i am from poor family", "i need scholarship", "general category student",
        "open category", "scholarship for higher studies", "financial assistance for education",
        "poor background student", "family income below", "economically weaker",
        "EWS category", "educational loan", "fee concession",
        "what is the eligibility", "eligibility for", "who is eligible",
        "am i qualified", "what are the requirements", "requirements for",
        "criteria for", "qualifications needed", "minimum qualification",
        "age limit", "income limit", "category requirement", "reservation",
        "percentage required", "marks required", "course eligibility",
        "degree eligibility", "education qualification", "work experience required",
        "eligibility criteria of", "eligible for this", "qualification for"
    ],
    "APPLICATION": [
        "how to apply", "application process", "registration process",
        "how do i register", "application procedure", "where can i apply",
        "apply online", "offline application", "application form",
        "how to register", "step by step application", "apply for this scheme"
    ],
    "DOCUMENTS": [
        "required documents", "what documents are needed",
        "which certificates are required", "document list",
        "proof required", "documents needed", "supporting documents",
        "certificates required", "document checklist"
    ],
    "BENEFITS": [
        "what are the benefits", "financial assistance",
        "how much amount will i get", "benefits of this scheme",
        "what support is provided", "what help will i receive",
        "scheme benefits", "assistance amount", "subsidy",
        "financial help", "what do i get", "benefits of"
    ],
    "RECOMMENDATION": [
        "recommend a scheme", "suggest a scheme", "best scheme for me",
        "which scheme should i choose", "best scholarship",
        "recommendation", "suggest", "which one is best",
        "advice on schemes", "help me choose", "suggest me schemes",
        "recommend me", "what schemes are available for me",
        "schemes for farmers", "schemes for women", "schemes for students",
        "schemes for", "available for", "for farmers", "for women",
        "for youth", "schemes in gujarat", "schemes in tamil nadu",
        "schemes applicable", "schemes relevant",
        "which scheme", "which scholarship", "choose a scheme"
    ],
    "SCHEME_SEARCH": [
        "tell me about ayushman bharat", "what is pm jay",
        "government schemes for women", "scholarships for engineering students",
        "farmer welfare schemes", "healthcare schemes in gujarat",
        "available government schemes", "schemes for farmers",
        "women empowerment schemes", "youth schemes", "employment schemes",
        "list of schemes", "tell me about", "what is", "explain",
        "tell me about scheme", "details about", "information about",
        "describe", "overview of", "about this scheme"
    ]
}

# Build embedding cache
intent_texts = []
intent_labels = []

for intent, examples in INTENT_EXAMPLES.items():
    for ex in examples:
        intent_texts.append(ex)
        intent_labels.append(intent)

intent_embeddings = model.encode(
    intent_texts,
    convert_to_numpy=True
)

def detect_intent(query, threshold=0.35, return_confidence=False):
    """
    Enhanced intent detection with comprehensive keyword-based pre-filtering.
    
    Returns:
        intent_name or (intent_name, confidence_score)
    """
    
    # Pre-filter with keyword matching for better accuracy
    query_lower = query.lower()
    
    # Check for specific scheme name mentions first (strongest signal)
    scheme_name_patterns = [
        r'mukhyamantri', r'mysy', r'pmjay', r'ayushman', r'pm kisan',
        r'pm awas', r'swavalamban', r'yuva', r'kisan', r'farmer'
    ]
    
    has_scheme_name = any(re.search(pattern, query_lower) for pattern in scheme_name_patterns)
    has_scheme_word = 'scheme' in query_lower
    has_tell_about = any(phrase in query_lower for phrase in [
        'tell me about', 'tell about', 'what is', 'details about', 
        'information about', 'describe', 'explain'
    ])
    
    # CRITICAL FIX: If query has a scheme name and is asking for information, it's SCHEME_SEARCH
    if has_scheme_name and (has_tell_about or has_scheme_word):
        if return_confidence:
            return ("SCHEME_SEARCH", 0.85)
        return "SCHEME_SEARCH"
    
    # Check for "scheme" + "tell me about" pattern - should be SCHEME_SEARCH
    if has_scheme_word and has_tell_about:
        if return_confidence:
            return ("SCHEME_SEARCH", 0.80)
        return "SCHEME_SEARCH"
    
    # Strong keyword indicators with priority order
    keyword_intents = {
        "ELIGIBILITY": [
            "eligible", "eligibility", "qualify", "can i", "am i", "do i",
            "poor family", "below poverty", "economically", "income",
            "general category", "open category", "sc/st", "obc", "ews",
            "scholarship", "financial assistance", "fee concession",
            "what is the eligibility", "eligibility for", "who is eligible",
            "am i qualified", "what are the requirements", "requirements for",
            "criteria for", "qualifications needed", "minimum qualification",
            "age limit", "income limit", "category requirement", "reservation",
            "percentage required", "marks required", "course eligibility",
            "degree eligibility", "education qualification", "work experience",
            "who can", "who cannot", "conditions to", "prerequisites",
            "eligibility criteria for", "eligibility of", "eligible for",
            "qualification for", "required for", "criteria of"
        ],
        "BENEFITS": [
            "benefit", "financial", "amount", "get", "receive", "assistance",
            "what are the benefits", "benefits of", "how much", "grant",
            "allowance", "support", "help", "what do i get", "subsidy"
        ],
        "APPLICATION": [
            "apply", "application", "register", "form", "process",
            "how to apply", "application process", "registration"
        ],
        "DOCUMENTS": [
            "document", "certificate", "proof", "required",
            "documents needed", "document list", "certificates required"
        ],
        "RECOMMENDATION": [
            "recommend", "suggest", "best", "which should", "help me choose",
            "which one", "choose", "advice", "suitable for me",
            "recommendation", "suggest me"
        ]
    }
    
    # Check for strong keyword matches with priority
    for intent, keywords in keyword_intents.items():
        # Count matching keywords
        match_count = sum(1 for k in keywords if k in query_lower)
        
        # If multiple keywords match, return that intent
        if match_count >= 2:
            # Check if this is actually a scheme search query
            if has_scheme_name and has_tell_about and intent != "SCHEME_SEARCH":
                if return_confidence:
                    return ("SCHEME_SEARCH", 0.85)
                return "SCHEME_SEARCH"
            
            # Use embedding for confidence but with boosted score
            query_embedding = model.encode(query, convert_to_numpy=True)
            similarities = cosine_similarity([query_embedding], intent_embeddings)[0]
            
            intent_scores = {}
            for intent_name in INTENT_EXAMPLES:
                indices = [i for i, label in enumerate(intent_labels) if label == intent_name]
                score = np.mean(similarities[indices])
                intent_scores[intent_name] = float(score)
            
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
            
            # Boost score for the matched intent
            if best_intent == intent:
                best_score = min(best_score + 0.15, 0.95)
            
            if best_score >= threshold:
                if return_confidence:
                    return (best_intent, float(best_score))
                return best_intent

    # Fallback to embedding-based detection
    query_embedding = model.encode(query, convert_to_numpy=True)
    similarities = cosine_similarity([query_embedding], intent_embeddings)[0]

    intent_scores = {}
    for intent_name in INTENT_EXAMPLES:
        indices = [i for i, label in enumerate(intent_labels) if label == intent_name]
        score = np.mean(similarities[indices])
        intent_scores[intent_name] = float(score)

    # Sort by score
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = sorted_intents[0]
    
    # Check if second best is close
    if len(sorted_intents) > 1:
        second_score = sorted_intents[1][1]
        if best_score - second_score < 0.05:
            # If scores are close, check keyword evidence again
            for intent, keywords in keyword_intents.items():
                if any(keyword in query_lower for keyword in keywords):
                    if intent != best_intent and second_score > threshold:
                        if return_confidence:
                            return (intent, float(second_score))
                        return intent

    # Multiple intent detection for complex queries
    secondary_intents = [
        (intent, float(score)) for intent, score in sorted_intents[1:3] 
        if score > threshold * 0.8
    ]
    
    # Convert secondary intents to Python floats for JSON serialization
    secondary_intents = [(intent, float(score)) for intent, score in secondary_intents]
    print(f"SECONDARY INTENTS: {secondary_intents}")

    if best_score < threshold:
        if return_confidence:
            return ("SCHEME_SEARCH", float(best_score))
        return "SCHEME_SEARCH"

    if return_confidence:
        return (best_intent, float(best_score))
    return best_intent