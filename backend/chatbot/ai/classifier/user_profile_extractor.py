import re
from typing import Dict, List, Optional

class UserProfileExtractor:
    """Extract user profile information from query text"""
    
    # State mappings - use word boundaries to avoid partial matches
    STATE_MAPPINGS = {
        'gujarat': [r'\bgujarat\b', r'\bgj\b', r'\bgujju\b'],
        'maharashtra': [r'\bmaharashtra\b', r'\bmh\b', r'\bmaharashtrian\b'],
        'tamil nadu': [r'\btamil nadu\b', r'\btn\b', r'\btamilnadu\b'],
        'karnataka': [r'\bkarnataka\b', r'\bka\b', r'\bkannada\b'],
        'kerala': [r'\bkerala\b', r'\bkl\b', r'\bkeralite\b'],
        'rajasthan': [r'\brajasthan\b', r'\brj\b', r'\brajasthani\b'],
        'delhi': [r'\bdelhi\b', r'\bdl\b', r'\bdelhite\b'],
        'uttar pradesh': [r'\buttar pradesh\b', r'\bup\b', r'\bupite\b'],
        'west bengal': [r'\bwest bengal\b', r'\bwb\b', r'\bbengali\b'],
        'bihar': [r'\bbihar\b', r'\bbr\b', r'\bbihari\b'],
        'punjab': [r'\bpunjab\b', r'\bpb\b', r'\bpunjabi\b'],
        'madhya pradesh': [r'\bmadhya pradesh\b', r'\bmp\b', r'\bmadhya\b'],
        'andhra pradesh': [r'\bandhra pradesh\b', r'\bap\b', r'\bandhra\b'],
        'telangana': [r'\btelangana\b', r'\btg\b', r'\btelugu\b'],
        'odisha': [r'\bodisha\b', r'\borissa\b', r'\boriya\b'],
        'assam': [r'\bassam\b', r'\bas\b', r'\bassamese\b'],
        'himachal pradesh': [r'\bhimachal pradesh\b', r'\bhp\b'],
        'uttarakhand': [r'\buttarakhand\b', r'\buk\b'],
        'jharkhand': [r'\bjharkhand\b', r'\bjh\b'],
        'chhattisgarh': [r'\bchhattisgarh\b', r'\bcg\b'],
        'goa': [r'\bgoa\b', r'\bga\b'],
        'pondicherry': [r'\bpondicherry\b', r'\bpy\b', r'\bpuducherry\b']
    }
    
    # Category mappings - use word boundaries
    # In user_profile_extractor.py - Update CATEGORY_MAPPINGS

    CATEGORY_MAPPINGS = {
        'general': [r'\bgeneral\b', r'\bopen\b', r'\bunreserved\b', r'\bgen\b', r'\bgeneral category\b'],
        'sc': [r'\bsc\b', r'\bscheduled caste\b', r'\bdalit\b'],
        'st': [r'\bst\b', r'\bscheduled tribe\b', r'\badivasi\b'],
        'obc': [r'\bobc\b', r'\bother backward class\b', r'\bbackward class\b'],
        'ews': [r'\bews\b', r'\beconomically weaker\b', r'\beconomically weaker section\b'],
        'minority': [r'\bminority\b', r'\bmuslim\b', r'\bchristian\b', r'\bsikh\b', r'\bbuddhist\b', r'\bjain\b', r'\bparsi\b']
    }
    
    # Education level mappings - use word boundaries
    EDUCATION_MAPPINGS = {
        'school': [r'\bschool\b', r'\bclass\b', r'\bstandard\b', r'\bsecondary\b', r'\bhigher secondary\b', r'\b10th\b', r'\b12th\b'],
        'graduation': [r'\bgraduation\b', r'\bgraduate\b', r'\bdegree\b', r'\bbachelor\b', r'\bbsc\b', r'\bba\b', r'\bbcom\b', r'\bbtech\b', r'\bbe\b', r'\bbca\b', r'\bbba\b'],
        'post_graduation': [r'\bpost graduation\b', r'\bpostgraduate\b', r'\bmaster\b', r'\bmsc\b', r'\bma\b', r'\bmcom\b', r'\bmtech\b', r'\bme\b', r'\bmba\b', r'\bmca\b'],
        'diploma': [r'\bdiploma\b', r'\bpolytechnic\b', r'\biti\b'],
        'phd': [r'\bphd\b', r'\bdoctorate\b', r'\bresearch\b']
    }
    
    # Gender mappings - use word boundaries
    GENDER_MAPPINGS = {
        'male': [r'\bmale\b', r'\bboy\b', r'\bman\b', r'\bhe\b', r'\bhim\b'],
        'female': [r'\bfemale\b', r'\bgirl\b', r'\bwoman\b', r'\bshe\b', r'\bher\b']
    }
    
    def __init__(self):
        self.state = None
        self.category = None
        self.education = None
        self.gender = None
        self.income = None
    
    def extract(self, query: str) -> Dict[str, Optional[str]]:
        """Extract all user profile information from query"""
        query_lower = query.lower()
        
        # Extract education first
        education = self._extract_education(query_lower)
        
        # If "student" is mentioned but no education level detected
        if not education and 'student' in query_lower:
            # Check for school-related keywords
            if any(word in query_lower for word in ['school', 'class', '10th', '12th', 'secondary']):
                education = 'school'
            # Check for graduation-related keywords
            elif any(word in query_lower for word in ['graduation', 'graduate', 'degree', 'college', 'university']):
                education = 'graduation'
            # Check for post-graduation
            elif any(word in query_lower for word in ['postgraduate', 'master', 'phd', 'doctorate']):
                education = 'post_graduation'
            # Check for diploma
            elif any(word in query_lower for word in ['diploma', 'polytechnic']):
                education = 'diploma'
            # Default for any other student mention
            else:
                education = 'graduation'
        
        return {
            'state': self._extract_state(query_lower),
            'category': self._extract_category(query_lower),
            'education': education,
            'gender': self._extract_gender(query_lower),
            'income': self._extract_income(query_lower)
        }
    
    def _extract_state(self, query: str) -> Optional[str]:
        """Extract state from query using regex with word boundaries"""
        for state, patterns in self.STATE_MAPPINGS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return state
        return None
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract category from query using regex with word boundaries"""
        for category, patterns in self.CATEGORY_MAPPINGS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return category
        return None
    
    def _extract_education(self, query: str) -> Optional[str]:
        """Extract education level from query using regex with word boundaries"""
        for level, patterns in self.EDUCATION_MAPPINGS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return level
        return None
    
    def _extract_gender(self, query: str) -> Optional[str]:
        """Extract gender from query using regex with word boundaries"""
        for gender, patterns in self.GENDER_MAPPINGS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return gender
        return None
    
    def _extract_income(self, query: str) -> Optional[str]:
        """Extract income from query"""
        income_patterns = [
            r'income\s*(?:below|less than|under|is)\s*([\d,]+)',
            r'([\d,]+)\s*(?:lakh|rupees|rs)',
            r'below\s*([\d,]+)',
            r'less than\s*([\d,]+)'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).replace(',', '')
        return None

# Global instance
profile_extractor = UserProfileExtractor()