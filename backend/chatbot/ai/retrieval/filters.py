def filter_results(

    results,

    threshold=0.42
):

    filtered = []


    for result in results:

        if result['score'] >= threshold:

            filtered.append(result)


    return filtered