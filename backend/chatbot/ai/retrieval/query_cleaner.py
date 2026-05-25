import re


def clean_query(
    query
):

    query = query.lower()


    query = re.sub(

        r'[^\w\s\u0A80-\u0AFF]',

        ' ',

        query
    )


    query = re.sub(

        r'\s+',

        ' ',

        query
    ).strip()


    return query