def detect_intent(query):

    q = query.lower().strip()

    if any(word in q for word in [
        'apply',
        'application',
        'how to apply',
        'registration'
    ]):
        return 'application'

    if any(word in q for word in [
        'eligibility',
        'eligible',
        'who can apply',
        'criteria',
        'requirement'
    ]):
        return 'eligibility'

    if any(word in q for word in [
        'document',
        'documents',
        'certificate',
        'proof'
    ]):
        return 'documents'

    if any(word in q for word in [
        'benefit',
        'benefits',
        'amount',
        'scholarship amount'
    ]):
        return 'benefits'

    if any(word in q for word in [
        'recommend',
        'suggest',
        'best scheme',
        'another',
        'other scheme',
        'more',
        'next'
    ]):
        return 'recommendation'

    return 'new_query'