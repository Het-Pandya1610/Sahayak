from typing import List, Dict, Any
from .query_cleaner import clean_query

def get_score(result, default=0.0):
    """Safely get score from result dict"""
    return result.get('boosted_score', result.get('rerank_score', result.get('score', default)))

def filter_results(results, threshold=0.42):
    """Basic score-based filtering"""
    filtered = []
    for result in results:
        score = get_score(result)
        if score >= threshold:
            filtered.append(result)
    return filtered

def check_category_match(scheme_data, user_category):
    """
    ULTRA STRICT category matching - completely removes mismatched categories
    """
    if not user_category:
        return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # Convert everything to lowercase for case-insensitive matching
    scheme_category = str(scheme_data.get('schemeCategory', '')).lower()
    eligibility = str(scheme_data.get('eligibility', '')).lower()
    scheme_name = str(scheme_data.get('scheme_name', '')).lower()
    level = str(scheme_data.get('level', '')).lower()
    
    # Combine all text for checking
    full_text = f"{scheme_category} {eligibility} {scheme_name} {level}"
    
    # Category keywords - more comprehensive
    category_keywords = {
        'sc': [
            'scheduled caste', 'scheduled castes', 'sc', 'sc/st', 'sc and st', 
            'sc st', 'dalit', 'sc category', 'sc candidate', 'sc students'
        ],
        'st': [
            'scheduled tribe', 'scheduled tribes', 'st', 'adivasi', 'tribal',
            'st category', 'st candidate', 'st students'
        ],
        'obc': [
            'other backward class', 'backward class', 'obc', 'obc category',
            'obc candidate', 'obc students'
        ],
        'ews': [
            'economically weaker', 'economically weaker section', 'ews',
            'ews category', 'ews candidate'
        ],
        'general': [
            'general', 'general category', 'open', 'unreserved', 'gen',
            'general candidate', 'open category'
        ]
    }
    
    # Check which categories the scheme is for
    scheme_categories = []
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in full_text:
                scheme_categories.append(category)
                break
    
    # If scheme mentions any reserved category
    reserved_categories = ['sc', 'st', 'obc', 'ews']
    scheme_has_reserved = any(cat in scheme_categories for cat in reserved_categories)
    
    # If user is GENERAL
    if user_category == 'general':
        # If scheme mentions ANY reserved category, SKIP IT
        if scheme_has_reserved:
            return {'match': False, 'penalty': 1.0, 'skip': True}
        
        # If scheme explicitly mentions GENERAL, it's a match
        if 'general' in scheme_categories:
            return {'match': True, 'penalty': 0.0, 'skip': False}
        
        # If scheme doesn't mention any category, it's open to all
        if not scheme_categories:
            return {'match': False, 'penalty': 0.0, 'skip': False}
        
        # Default: allow if no reserved categories mentioned
        return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # If user is in a reserved category
    if user_category in reserved_categories:
        # If scheme mentions user's category, it's a match
        if user_category in scheme_categories:
            return {'match': True, 'penalty': 0.0, 'skip': False}
        
        # If scheme mentions a different reserved category, skip it
        if scheme_has_reserved:
            return {'match': False, 'penalty': 1.0, 'skip': True}
        
        # If scheme doesn't mention any category, it's open
        if not scheme_categories:
            return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # Default
    return {'match': False, 'penalty': 0.0, 'skip': False}

def check_education_match(scheme_data, user_education):
    """Check if scheme matches user's education level"""
    if not user_education:
        return {'match': False, 'penalty': 0.0}
    
    eligibility = str(scheme_data.get('eligibility', '')).lower()
    scheme_category = str(scheme_data.get('schemeCategory', '')).lower()
    
    # Education keywords
    edu_keywords = {
        'school': ['school', 'class', '10th', '12th', 'secondary', 'higher secondary', 'primary'],
        'graduation': ['graduation', 'graduate', 'degree', 'bachelor', 'undergraduate', 'college', 'university'],
        'post_graduation': ['post graduate', 'postgraduate', 'master', 'phd', 'doctorate', 'mba', 'mca'],
        'diploma': ['diploma', 'polytechnic', 'vocational', 'iti']
    }
    
    # Check if scheme is education-related
    is_education_scheme = False
    edu_terms = ['education', 'student', 'scholarship', 'learning', 'school', 'college', 'university']
    for term in edu_terms:
        if term in scheme_category:
            is_education_scheme = True
            break
    
    if not is_education_scheme:
        return {'match': False, 'penalty': 0.0}
    
    # Check if user's education level matches
    matched = False
    for level, keywords in edu_keywords.items():
        if user_education == level:
            for keyword in keywords:
                if keyword in eligibility:
                    matched = True
                    break
        if matched:
            break
    
    if matched:
        return {'match': True, 'penalty': 0.0}
    
    # Check if scheme mentions any education level
    scheme_has_education = False
    for level, keywords in edu_keywords.items():
        for keyword in keywords:
            if keyword in eligibility:
                scheme_has_education = True
                break
        if scheme_has_education:
            break
    
    if scheme_has_education:
        return {'match': False, 'penalty': 0.4}
    
    return {'match': False, 'penalty': 0.0}

def check_state_match(scheme_data, user_state):
    """Check if scheme matches user's state"""
    if not user_state:
        return {'match': False, 'penalty': 0.0}
    
    level = str(scheme_data.get('level', '')).lower()
    eligibility = str(scheme_data.get('eligibility', '')).lower()
    
    # Central schemes are for everyone
    if 'central' in level or 'central' in eligibility:
        return {'match': False, 'penalty': 0.0}
    
    # Check if user's state matches
    if user_state in level or user_state in eligibility:
        return {'match': True, 'penalty': 0.0}
    
    return {'match': False, 'penalty': 0.3}

def check_gender_match(scheme_data, user_gender):
    """Check if scheme matches user's gender"""
    if not user_gender:
        return {'match': False, 'penalty': 0.0}
    
    eligibility = str(scheme_data.get('eligibility', '')).lower()
    scheme_name = str(scheme_data.get('scheme_name', '')).lower()
    category = str(scheme_data.get('schemeCategory', '')).lower()
    
    female_terms = ['girl', 'woman', 'female', 'women', 'girls', 'ladies', 'she', 'her']
    male_terms = ['boy', 'man', 'male', 'men', 'boys', 'gentlemen', 'he', 'him']
    
    is_female_scheme = False
    for term in female_terms:
        if term in eligibility or term in scheme_name or term in category:
            is_female_scheme = True
            break
    
    is_male_scheme = False
    for term in male_terms:
        if term in eligibility or term in scheme_name or term in category:
            is_male_scheme = True
            break
    
    if user_gender == 'female':
        if is_female_scheme:
            return {'match': True, 'penalty': 0.0}
        elif is_male_scheme:
            return {'match': False, 'penalty': 0.5}
    else:  # male
        if is_male_scheme:
            return {'match': True, 'penalty': 0.0}
        elif is_female_scheme and not is_male_scheme:
            return {'match': False, 'penalty': 0.5}
    
    return {'match': False, 'penalty': 0.0}

def filter_by_profile(results, profile: Dict[str, Any], boost_factor: float = 0.15):
    """
    Filter and boost results based on user profile - ULTRA STRICT VERSION
    """
    if not results or not profile:
        return results
    
    boosted_results = []
    
    for result in results:
        scheme = result['scheme']
        
        # Extract scheme data
        if isinstance(scheme, dict):
            scheme_data = scheme
        else:
            scheme_data = {
                'scheme_name': scheme.scheme_name,
                'schemeCategory': scheme.schemeCategory,
                'level': scheme.level,
                'eligibility': scheme.eligibility,
                'details': scheme.details
            }
        
        boost = 0.0
        matches = []
        penalty = 0.0
        skip = False
        
        # ============================================================
        # ULTRA STRICT CATEGORY FILTERING
        # ============================================================
        if profile.get('category'):
            cat_result = check_category_match(scheme_data, profile['category'])
            
            # If skip is True, completely remove this scheme
            if cat_result.get('skip', False):
                continue
            
            if cat_result['match']:
                boost += boost_factor * 1.5
                matches.append('category')
            else:
                penalty += cat_result['penalty']
        
        # ============================================================
        # EDUCATION FILTERING
        # ============================================================
        if profile.get('education'):
            edu_result = check_education_match(scheme_data, profile['education'])
            if edu_result['match']:
                boost += boost_factor * 1.2
                matches.append('education')
            penalty += edu_result['penalty']
        
        # ============================================================
        # STATE FILTERING
        # ============================================================
        if profile.get('state'):
            state_result = check_state_match(scheme_data, profile['state'])
            if state_result['match']:
                boost += boost_factor * 1.5
                matches.append('state')
            penalty += state_result['penalty']
        
        # ============================================================
        # GENDER FILTERING
        # ============================================================
        if profile.get('gender'):
            gender = profile['gender'].lower()
            eligibility = str(scheme_data.get('eligibility', '')).lower()
            scheme_name = str(scheme_data.get('scheme_name', '')).lower()
            category = str(scheme_data.get('schemeCategory', '')).lower()
            
            female_terms = ['girl', 'woman', 'female', 'women', 'girls', 'ladies', 'she', 'her', 'daughter']
            male_terms = ['boy', 'man', 'male', 'men', 'boys', 'gentlemen', 'he', 'him', 'son']
            
            is_female_scheme = False
            for term in female_terms:
                if term in eligibility or term in scheme_name or term in category:
                    is_female_scheme = True
                    break
            
            is_male_scheme = False
            for term in male_terms:
                if term in eligibility or term in scheme_name or term in category:
                    is_male_scheme = True
                    break
            
            if gender == 'male' and is_female_scheme and not is_male_scheme:
                continue
            if gender == 'female' and is_male_scheme and not is_female_scheme:
                continue
            
            if (gender == 'male' and is_male_scheme) or (gender == 'female' and is_female_scheme):
                boost += boost_factor * 1.5
                matches.append('gender')
        
        # ============================================================
        # CALCULATE FINAL SCORE
        # ============================================================
        original_score = get_score(result)
        boosted_score = max(0.0, min(original_score + boost - penalty, 0.99))
        
        # Skip if penalty is too high
        if penalty > 0.5 and len(matches) == 0:
            continue
        
        result['boosted_score'] = boosted_score
        result['profile_matches'] = matches
        result['profile_boost'] = boost
        result['penalty'] = penalty
        
        boosted_results.append(result)
    
    # Sort by boosted score
    boosted_results.sort(key=lambda x: x.get('boosted_score', 0), reverse=True)
    
    # Remove results with score < 0.3
    final_results = []
    for r in boosted_results:
        if r.get('boosted_score', 0) >= 0.3:
            final_results.append(r)
    
    return final_results

def filter_and_rank(results, profile=None, threshold=0.35):
    """
    Combined filtering and ranking with profile-based boosting
    """
    filtered = filter_results(results, threshold)
    
    if not filtered:
        return []
    
    if profile and any(profile.values()):
        filtered = filter_by_profile(filtered, profile)
    
    if not filtered:
        return filter_results(results, threshold * 0.8)
    
    return filtered