# chatbot/ai/memory/conversation_memory.py

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

MAX_HISTORY = 10
MAX_CONTEXT_TOKENS = 2000

class ConversationMemory:
    """Enhanced conversation memory with context tracking"""
    
    def __init__(self):
        self.history = []
        self.context = {
            'last_schemes': [],      # Last shown schemes
            'last_intent': None,     # Last detected intent
            'current_query': None,   # Current query
            'extracted_entities': {}, # Entities from conversation
            'conversation_flow': []   # Flow tracking
        }
    
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
            scheme_names = [s.get('scheme_name', s) if isinstance(s, dict) else str(s) for s in schemes[:5]]
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
        
        # Check for follow-up indicators
        follow_up_keywords = [
            'how to apply for', 'apply for number', 'tell me about', 
            'what about', 'explain', 'details for', 'scheme number',
            'how do i', 'what is the process', 'where do i'
        ]
        
        import re
        scheme_number_match = re.search(r'(?:number|no|#|scheme)\s*(\d+)', query_lower)
        if scheme_number_match:
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['referenced_scheme'] = int(scheme_number_match.group(1))
            context['needs_scheme_reference'] = True


        if any(word in query_lower.split() for word in ['that', 'it', 'this', 'those', 'these']):
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['needs_scheme_reference'] = True
            if context['referenced_scheme'] is None:
                context['referenced_scheme'] = 1
    
        if 'the scheme' in query_lower or 'this scheme' in query_lower:
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
            context['needs_scheme_reference'] = True
            if context['referenced_scheme'] is None:
                context['referenced_scheme'] = 1
            
        # Check for words that reference previous context
        reference_keywords = ['it', 'that', 'this', 'those', 'these', 'them', 'its']
        if any(keyword in query_lower.split() for keyword in reference_keywords):
            context['is_follow_up'] = True
            context['refers_to_previous'] = True
        
        # Check if it's asking about a scheme from previous response
        if any(keyword in query_lower for keyword in follow_up_keywords):
            context['is_follow_up'] = True
            context['needs_scheme_reference'] = True
        
        # Check for application/process related follow-up
        application_keywords = ['apply', 'application', 'process', 'register', 'form']
        if any(keyword in query_lower for keyword in application_keywords):
            context['referenced_intent'] = 'APPLICATION'
            if not scheme_number_match:
                context['needs_scheme_reference'] = True
        
        # Check for eligibility follow-up
        eligibility_keywords = ['eligible', 'eligibility', 'qualify', 'can i']
        if any(keyword in query_lower for keyword in eligibility_keywords):
            context['referenced_intent'] = 'ELIGIBILITY'
            if not scheme_number_match:
                context['needs_scheme_reference'] = True
        
        # Check for benefits follow-up
        benefits_keywords = ['benefit', 'benefits', 'amount', 'get', 'receive']
        if any(keyword in query_lower for keyword in benefits_keywords):
            context['referenced_intent'] = 'BENEFITS'
            if not scheme_number_match:
                context['needs_scheme_reference'] = True
        
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
    
    def clear(self):
        """Clear conversation memory"""
        self.history = []
        self.context = {
            'last_schemes': [],
            'last_intent': None,
            'current_query': None,
            'extracted_entities': {},
            'conversation_flow': []
        }


# Singleton instance
_conversation_memory = None

def get_conversation_memory():
    """Get singleton conversation memory instance"""
    global _conversation_memory
    if _conversation_memory is None:
        _conversation_memory = ConversationMemory()
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