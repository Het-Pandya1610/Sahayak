from chatbot.ai.classifier.intent_detector import detect_intent


def generate_response(query, results, history=None):

    if history is None:
        history = []


    if not results:

        return {

            'success': False,

            'answer':
                "Sorry, I couldn't find any relevant government scheme for your query.",

            'schemes': []
        }


    top_scheme = results[0]['scheme']


    confidence = min(
        round(
            results[0]['rerank_score'] * 100,2
        ),
        99.0
    )


    # Conversational intro
    intro = ""

    intent = detect_intent(query)

    print("=" * 50)
    print("QUERY:", query)
    print("INTENT:", intent)
    print("=" * 50)

    if intent == "recommendation":

        recommendations = []

        for item in results[:5]:

            scheme = item['scheme']

            recommendations.append(
                f"""
                • {scheme['scheme_name']}
                Category: {scheme.get('schemeCategory', 'N/A')}
                Level: {scheme.get('level', 'N/A')}
                """
            )

        detailed_answer = (
            "Based on your profile, I found these relevant schemes:\n\n"
            + "\n".join(recommendations)
        )

    elif intent == "eligibility":

        intro = (
            f"Based on your question, you may be eligible for "
            f"'{top_scheme['scheme_name']}'."
        )

        detailed_answer = f"""
            {intro}\n

            Eligibility Criteria:\n
            {top_scheme.get('eligibility', 'Not available')}
        """
            

    elif intent == "documents":

        intro = (
            f"Here are the required documents for "
            f"'{top_scheme['scheme_name']}'."
        )

        detailed_answer = f"""
            {intro}\n
            Required Documents:\n
            {top_scheme.get('documents', 'Not available')}
        """

    elif intent == "application":

        intro = (
            f"Here's how you can apply for "
            f"'{top_scheme['scheme_name']}'."
        )

        detailed_answer = f"""
            {intro}\n

            Application Process:\n
            {top_scheme.get('application', 'Not available')}
        """

    else:

        intro = (
            f"I found a relevant government scheme: "
            f"'{top_scheme['scheme_name']}'."
        )


        detailed_answer = f"""
        {intro}\n

        Benefits:\n
        {top_scheme.get('benefits', 'Not available')}\n

        Eligibility:\n
        {top_scheme.get('eligibility', 'Not available')}\n

        Application Process:\n
        {top_scheme.get('application', 'Not available')}\n

        Required Documents:\n
        {top_scheme.get('documents', 'Not available')}
        """


    response = {

        'success': True,

        'answer':
            detailed_answer.strip(),

        'confidence':
            confidence,

        'intent':
            intent,

        'schemes': []
    }


    for item in results[:5]:

        scheme = item['scheme']


        response['schemes'].append({

            'scheme_name':
                scheme.get('scheme_name', ''),

            'details':
                scheme.get('details', ''),

            'benefits':
                scheme.get('benefits', ''),

            'eligibility':
                scheme.get('eligibility', ''),

            'application':
                scheme.get('application', ''),

            'documents':
                scheme.get('documents', ''),

            'category':
                scheme.get('schemeCategory', ''),

            'level':
                scheme.get('level', ''),

            'score':
                round(item['rerank_score'], 3)
        })


    return response