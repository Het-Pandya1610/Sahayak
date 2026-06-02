from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from chatbot.ai.chatbot_engine.pipeline import chatbot_pipeline

@csrf_exempt
def chatbot_response(request):

    if request.method != 'POST':

        return JsonResponse({

            'error':
                'POST request required'

        }, status=400)


    try:

        body = json.loads(
            request.body
        )

        query = body.get(
            'query',
            ''
        )


        if not query:

            return JsonResponse({

                'error':
                    'Query is required'

            }, status=400)


        history = body.get('history', [])

        response = chatbot_pipeline(
            query,
            history
        )


        return JsonResponse(
            response,
            safe=False
        )


    except Exception as e:

        print("CHATBOT ERROR:", str(e))

        return JsonResponse({

            'success': False,

            'error': str(e)

        }, status=500)