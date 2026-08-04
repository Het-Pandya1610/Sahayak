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

def check_category_match_scheme(scheme_data, user_category):
    """
    Check if scheme matches user's category using pre-extracted data
    FAST and ACCURATE - no regex needed!
    """
    if not user_category:
        return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # Get pre-extracted categories from the scheme
    extracted_categories = scheme_data.get('extracted_categories', [])
    is_category_specific = scheme_data.get('is_category_specific', False)
    primary_category = scheme_data.get('primary_category', '')
    
    # If no categories extracted, scheme is open to all
    if not extracted_categories:
        return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # Define reserved categories
    reserved_categories = ['sc', 'st', 'obc', 'ews']
    
    # Check if scheme has any reserved category
    has_reserved = any(cat in extracted_categories for cat in reserved_categories)
    
    # ============================================================
    # USER IS GENERAL CATEGORY
    # ============================================================
    if user_category == 'general':
        # If scheme has reserved categories, SKIP IT
        if has_reserved:
            return {'match': False, 'penalty': 1.0, 'skip': True}
        
        # If scheme has 'general' in categories, it's a match
        if 'general' in extracted_categories:
            return {'match': True, 'penalty': 0.0, 'skip': False}
        
        # If scheme has no specific category, it's open
        if not is_category_specific:
            return {'match': False, 'penalty': 0.0, 'skip': False}
        
        # Default: allow if no reserved categories
        return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # ============================================================
    # USER IS IN RESERVED CATEGORY (SC, ST, OBC, EWS)
    # ============================================================
    if user_category in reserved_categories:
        # If scheme explicitly mentions user's category, it's a MATCH
        if user_category in extracted_categories:
            return {'match': True, 'penalty': 0.0, 'skip': False}
        
        # If scheme has a different reserved category, SKIP IT
        other_reserved = [cat for cat in reserved_categories if cat in extracted_categories and cat != user_category]
        if other_reserved:
            return {'match': False, 'penalty': 1.0, 'skip': True}
        
        # If scheme has no category or is open, it's allowed
        if not extracted_categories or not is_category_specific:
            return {'match': False, 'penalty': 0.0, 'skip': False}
        
        # If scheme has 'general' in categories, it's allowed for reserved users too
        if 'general' in extracted_categories:
            return {'match': False, 'penalty': 0.0, 'skip': False}
    
    # ============================================================
    # USER IS IN OTHER SPECIAL CATEGORIES (Minority, Women, etc.)
    # ============================================================
    # For these, we check if scheme mentions any category
    if extracted_categories and is_category_specific:
        # If scheme is specific to a category that doesn't match user
        if user_category not in extracted_categories:
            # Check if scheme is for a different specific category
            if len(extracted_categories) == 1:
                # Scheme is only for one specific category
                return {'match': False, 'penalty': 0.5, 'skip': False}
    
    # Default: allow if no strict mismatch
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
    Filter and boost results based on user profile using extracted categories
    """
    if not results or not profile:
        return results
    
    boosted_results = []
    
    for result in results:
        scheme = result['scheme']
        
        # Extract scheme data - include extracted categories
        if isinstance(scheme, dict):
            scheme_data = scheme
        else:
            scheme_data = {
                'scheme_name': scheme.scheme_name,
                'schemeCategory': scheme.schemeCategory,
                'level': scheme.level,
                'eligibility': scheme.eligibility,
                'details': scheme.details,
                # Extracted category fields
                'extracted_categories': getattr(scheme, 'extracted_categories', []),
                'is_category_specific': getattr(scheme, 'is_category_specific', False),
                'primary_category': getattr(scheme, 'primary_category', ''),
            }
        
        boost = 0.0
        matches = []
        penalty = 0.0
        skip = False
        
        # ============================================================
        # FAST CATEGORY FILTERING USING EXTRACTED DATA
        # ============================================================
        if profile.get('category'):
            cat_result = check_category_match_scheme(scheme_data, profile['category'])
            
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