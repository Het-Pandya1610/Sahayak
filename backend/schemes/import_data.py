import pandas as pd # type: ignore
from schemes.models import Scheme


def clean(value):

    if pd.isna(value):

        return ''

    return str(value).strip()


def parse_tags(value):

    if pd.isna(value):

        return []

    return [

        tag.strip()

        for tag in str(value).split(',')

        if tag.strip()
    ]


def import_csv():

    file_path = (
        './datasets/updated_data.csv'
    )

    df = pd.read_csv(file_path)

    print(
        f'Total rows: {len(df)}'
    )

    schemes = []

    for _, row in df.iterrows():

        try:

            scheme = Scheme(

                scheme_name=clean(
                    row.get('scheme_name')
                ),

                slug=clean(
                    row.get('slug')
                ),

                details=clean(
                    row.get('details')
                ),

                benefits=clean(
                    row.get('benefits')
                ),

                eligibility=clean(
                    row.get('eligibility')
                ),

                application=clean(
                    row.get('application')
                ),

                documents=clean(
                    row.get('documents')
                ),

                level=clean(
                    row.get('level')
                ),

                schemeCategory=clean(
                    row.get(
                        'schemeCategory'
                    )
                ),

                tags=parse_tags(
                    row.get('tags')
                )
            )

            schemes.append(scheme)

        except Exception as e:

            print(
                f'Error: {e}'
            )

    if schemes:

        Scheme.objects.insert(
            schemes,
            load_bulk=False
        )

    print(
        f'Imported {len(schemes)} schemes successfully'
    )


if __name__ == '__main__':

    import_csv()