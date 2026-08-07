import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .memory_storage import get_memory_storage
import re

MAX_HISTORY = 10
MAX_CONTEXT_TOKENS = 2000

# Global cache for scheme names
_scheme_names_cache = None

def get_all_scheme_names():
    """Get all scheme names from database with caching"""
    global _scheme_names_cache
    if _scheme_names_cache is not None:
        return _scheme_names_cache
    
    try:
        from schemes.models import Scheme
        schemes = Scheme.objects.all()
        _scheme_names_cache = [scheme.scheme_name.lower() for scheme in schemes]
        print(f"📊 Loaded {len(_scheme_names_cache)} scheme names from database")
        return _scheme_names_cache
    except Exception as e:
        print(f"⚠️ Could not load scheme names from database: {e}")
        # Return empty list as fallback
        return []

def extract_scheme_names_from_query(query: str) -> List[str]:
    """
    Extract all scheme names mentioned in the query
    Returns list of scheme names found
    """
    query_lower = query.lower()
    found_names = []
    all_names = get_all_scheme_names()
    
    # Sort by length (longest first) to match full names properly
    sorted_names = sorted(all_names, key=len, reverse=True)
    
    for name in sorted_names:
        if name in query_lower:
            found_names.append(name)
            # Remove the found name from query to avoid partial matches
            # But we need to be careful with this
    
    return found_names

def has_explicit_scheme_in_query(query: str) -> bool:
    """Check if query contains any scheme name from database"""
    return len(extract_scheme_names_from_query(query)) > 0

class ConversationMemory:
    """Enhanced conversation memory with context tracking and persistence"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or 'default_session'
        self.history = []
        self.context = {
            'last_schemes': [],
            'last_intent': None,
            'current_query': None,
            'extracted_entities': {},
            'conversation_flow': [],
            'last_referenced_scheme': None,
        }
        
        # Try to load existing memory
        self._load_from_storage()
    
    def _load_from_storage(self):
        """Load memory from persistent storage"""
        try:
            storage = get_memory_storage()
            stored = storage.load_memory(self.session_id)
            if stored:
                self.history = stored.get('history', [])
                self.context = stored.get('context', self.context)
                print(f"📂 Loaded memory for session: {self.session_id} ({len(self.history)} messages)")
        except Exception as e:
            print(f"⚠️ Could not load memory: {e}")
    
    def _save_to_storage(self):
        """Save memory to persistent storage"""
        try:
            storage = get_memory_storage()
            storage.save_memory(self.session_id, {
                'history': self.history,
                'context': self.context
            })
        except Exception as e:
            print(f"⚠️ Could not save memory: {e}")
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to history with metadata"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.history.append(message)
        
        # Keep only last MAX_HISTORY messages
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
        
        # Save to storage
        self._save_to_storage()
    
    def update_context(self, query: str, intent: str, schemes: List = None, entities: Dict = None):
        """Update conversation context"""
        self.context['current_query'] = query
        self.context['last_intent'] = intent
        
        if schemes:
            self.context['last_schemes'] = schemes
            
        if entities:
            self.context['extracted_entities'].update(entities)
            
        self.context['conversation_flow'].append({
            'query': query,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 flow entries
        if len(self.context['conversation_flow']) > 10:
            self.context['conversation_flow'] = self.context['conversation_flow'][-10:]
        
        # Save to storage
        self._save_to_storage()
    
    def get_last_schemes(self) -> List:
        """Get the last shown schemes"""
        return self.context.get('last_schemes', [])
    
    def get_last_intent(self) -> str:
        """Get the last intent"""
        return self.context.get('last_intent')
    
    def build_context_string(self) -> str:
        """Build a context string for the LLM"""
        if not self.history:
            return ""
        
        context_parts = []
        
        # Add recent conversation
        for msg in self.history[-MAX_HISTORY:]:
            role = msg['role']
            content = msg['content']
            context_parts.append(f"{role}: {content}")
        
        # Add context about last schemes
        if self.context.get('last_schemes'):
            schemes = self.context['last_schemes']
            scheme_names = []
            for s in schemes[:5]:
                if isinstance(s, dict):
                    scheme_names.append(s.get('scheme_name', str(s)))
                else:
                    scheme_names.append(str(s))
            context_parts.append(f"Previously shown schemes: {', '.join(scheme_names)}")
        
        # Add extracted entities
        if self.context.get('extracted_entities'):
            entities = self.context['extracted_entities']
            entity_str = ', '.join([f"{k}: {v}" for k, v in entities.items() if v])
            if entity_str:
                context_parts.append(f"User profile: {entity_str}")
        
        return "\n".join(context_parts)
    
    def get_follow_up_context(self, query: str) -> Dict:
        """
        Analyze if a query is a follow-up and extract relevant context
        """
        context = {
            'is_follow_up': False,
            'refers_to_previous': False,
            'referenced_scheme': None,
            'referenced_intent': None,
            'needs_scheme_reference': False,
            'previous_query': None
        }
        
        query_lower = query.lower()
        
        # ============================================================
        # FIX: Check if query contains an explicit scheme name from database
        # If yes, it's NOT a follow-up
        # ============================================================
        has_explicit_scheme = has_explicit_scheme_in_query(query)
        
        if has_explicit_scheme:
            found_names = extract_scheme_names_from_query(query)
            print(f"📌 Query contains explicit scheme name(s): {found_names} - NOT a follow-up")
            return context
        
        # ============================================================
        # Check for "it", "that", "this" references (PRONOUNS)
        # ============================================================
        pronoun_keywords = ['it', 'that', 'this', 'those', 'these', 'them', 'its']
        has_pronoun = any(word in query_lower.split() for word in pronoun_keywords)
        
        if has_pronoun:
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['needs_scheme_reference'] = True
            if context['referenced_scheme'] is None:
                context['referenced_scheme'] = 1
            print(f"📌 Query contains pronoun - follow-up detected")
        
        # ============================================================
        # Check for scheme number references (#, no., number, scheme)
        # ============================================================
        scheme_number_match = re.search(r'(?:number|no\.?|#|scheme)\s*(\d+)', query_lower)
        if scheme_number_match:
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['referenced_scheme'] = int(scheme_number_match.group(1))
            context['needs_scheme_reference'] = True
            print(f"📌 Query contains scheme number - follow-up detected")
        
        # ============================================================
        # Check for "the scheme" or "this scheme"
        # ============================================================
        if 'the scheme' in query_lower or 'this scheme' in query_lower:
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['needs_scheme_reference'] = True
            if context['referenced_scheme'] is None:
                context['referenced_scheme'] = 1
            print(f"📌 Query contains 'the scheme' - follow-up detected")
        
        # ============================================================
        # Check for explicit intent (benefits, eligibility, apply)
        # Only if we already detected a follow-up above
        # ============================================================
        if context['is_follow_up']:
            # Check for application/process
            application_keywords = ['apply', 'application', 'process', 'register', 'form']
            if any(keyword in query_lower for keyword in application_keywords):
                context['referenced_intent'] = 'APPLICATION'
            
            # Check for eligibility
            eligibility_keywords = ['eligible', 'eligibility', 'qualify', 'can i']
            if any(keyword in query_lower for keyword in eligibility_keywords):
                context['referenced_intent'] = 'ELIGIBILITY'
            
            # Check for benefits
            benefits_keywords = ['benefit', 'benefits', 'amount', 'get', 'receive']
            if any(keyword in query_lower for keyword in benefits_keywords):
                context['referenced_intent'] = 'BENEFITS'
            
            # Check for documents
            documents_keywords = ['document', 'documents', 'paperwork', 'certificate']
            if any(keyword in query_lower for keyword in documents_keywords):
                context['referenced_intent'] = 'DOCUMENTS'
        
        # Get previous query from history
        if self.history:
            for msg in reversed(self.history):
                if msg['role'] == 'user':
                    context['previous_query'] = msg['content']
                    break
        
        return context

    def get_scheme_by_number(self, number: int) -> Optional[Dict]:
        """Get a scheme by its position in the last shown list (1-indexed)"""
        schemes = self.context.get('last_schemes', [])
        if 1 <= number <= len(schemes):
            return schemes[number - 1]
        return None

    def get_last_scheme(self) -> Optional[Dict]:
        """Get the last shown scheme"""
        schemes = self.context.get('last_schemes', [])
        if schemes:
            return schemes[0]
        return None

    def get_scheme_by_reference(self, reference_number: int = 1) -> Optional[Dict]:
        """Get scheme by reference number (1-indexed)"""
        schemes = self.context.get('last_schemes', [])
        if not schemes:
            return None
        
        if reference_number > len(schemes) or reference_number < 1:
            return schemes[0]
        
        return schemes[reference_number - 1]

    def has_schemes_in_memory(self) -> bool:
        """Check if there are any schemes in memory"""
        return bool(self.context.get('last_schemes', []))

    def clear(self):
        """Clear conversation memory"""
        self.history = []
        self.context = {
            'last_schemes': [],
            'last_intent': None,
            'current_query': None,
            'extracted_entities': {},
            'conversation_flow': [],
            'last_referenced_scheme': None
        }
        self._save_to_storage()

    def set_last_referenced_scheme(self, scheme_name: str, scheme_data: Dict = None):
        """Set the last scheme the user explicitly asked about"""
        self.context['last_referenced_scheme'] = {
            'name': scheme_name,
            'data': scheme_data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_to_storage()

    def get_last_referenced_scheme(self) -> Optional[Dict]:
        """Get the last scheme the user asked about"""
        return self.context.get('last_referenced_scheme')

    def clear_last_referenced_scheme(self):
        """Clear the last referenced scheme"""
        self.context['last_referenced_scheme'] = None
        self._save_to_storage()


# Singleton instance
_conversation_memory = None
_current_session_id = 'default_session'

def get_conversation_memory(session_id: str = None):
    """Get singleton conversation memory instance"""
    global _conversation_memory, _current_session_id
    
    # Use provided session_id or default
    session_id = session_id or 'default_session'
    
    # If session changed or no memory, create new
    if _conversation_memory is None or _current_session_id != session_id:
        _conversation_memory = ConversationMemory(session_id)
        _current_session_id = session_id
    
    return _conversation_memory

def build_conversation_context(history):
    """Legacy function for backward compatibility"""
    if not history:
        return ""
    
    context = ""
    for msg in history[-MAX_HISTORY:]:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        context += f"{role}: {content}\n"
    
    return context.strip()