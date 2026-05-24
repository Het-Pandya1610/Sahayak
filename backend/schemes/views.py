from django.http import JsonResponse
from bson import ObjectId

from schemes.models import Scheme


def get_schemes(request):

    page = int(
        request.GET.get('page', 1)
    )

    limit = int(
        request.GET.get('limit', 12)
    )

    search = request.GET.get(
        'search',
        ''
    )

    category = request.GET.get(
        'category',
        ''
    )

    level = request.GET.get(
        'level',
        ''
    )

    query = {}

    if search:

        query['scheme_name__icontains'] = search

    if category:

        query['schemeCategory__icontains'] = category

    if level:

        query['level__icontains'] = level

    schemes_queryset = (
        Scheme.objects(**query)
    )

    total = schemes_queryset.count()

    start = (page - 1) * limit

    end = start + limit

    schemes = schemes_queryset[
        start:end
    ]

    data = []

    for scheme in schemes:

        data.append({

            'id': str(scheme.id),

            'scheme_name':
                scheme.scheme_name,

            'slug':
                scheme.slug,

            'details':
                scheme.details[:180] + '...' if scheme.details else '',

            'benefits':
                scheme.benefits,

            'eligibility':
                scheme.eligibility,

            'application':
                scheme.application,

            'documents':
                scheme.documents,

            'level':
                scheme.level,

            'schemeCategory':
                scheme.schemeCategory,

            'tags':
                scheme.tags,
        })

    return JsonResponse({

        'total': total,

        'page': page,

        'limit': limit,

        'total_pages': (
            total + limit - 1
        ) // limit,

        'schemes': data

    })

def get_scheme_details(
    request,
    id
):

    try:

        scheme = Scheme.objects.get(
            id=ObjectId(id)
        )

        data = {

            'id': str(scheme.id),

            'scheme_name':
                scheme.scheme_name,

            'slug':
                scheme.slug,

            'details':
                scheme.details,

            'benefits':
                scheme.benefits,

            'eligibility':
                scheme.eligibility,

            'application':
                scheme.application,

            'documents':
                scheme.documents,

            'level':
                scheme.level,

            'schemeCategory':
                scheme.schemeCategory,

            'tags':
                scheme.tags,
        }

        return JsonResponse(data)

    except:

        return JsonResponse({

            'error':
                'Scheme not found'

        }, status=404)