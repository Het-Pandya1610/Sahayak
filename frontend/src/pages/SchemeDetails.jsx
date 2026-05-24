import React, {
    useEffect,
    useState
} from 'react';

import {
    useParams
} from 'react-router-dom';

import MainLayout from '../layouts/MainLayout';

import './css/SchemeDetails.css';

function SchemeDetails() {

    const { id } = useParams();

    const [scheme, setScheme] = useState(null);

    const [loading, setLoading] = useState(true);



    useEffect(() => {

        fetchScheme();

    }, [id]);



    const fetchScheme = async () => {

        try {

            const response = await fetch(

                `http://127.0.0.1:8000/api/schemes/${id}/`

            );

            const data = await response.json();

            setScheme(data);

        }

        catch (error) {

            console.error(error);

        }

        finally {

            setLoading(false);
        }
    };



    if (loading) {

        return (

            <MainLayout>

                <p className='loading-schemes'>
                    Loading...
                </p>

            </MainLayout>
        );
    }



    if (!scheme) {

        return (

            <MainLayout>

                <p>
                    Scheme not found
                </p>

            </MainLayout>
        );
    }



    return (

        <MainLayout>

            <div className="scheme-details-page">

                <h1>
                    {scheme.scheme_name}
                </h1>



                <div className="scheme-section">

                    <h2>
                        Details
                    </h2>

                    <p>
                        {scheme.details}
                    </p>

                </div>



                <div className="scheme-section">

                    <h2>
                        Benefits
                    </h2>

                    <p>
                        {scheme.benefits}
                    </p>

                </div>



                <div className="scheme-section">

                    <h2>
                        Eligibility
                    </h2>

                    <p>
                        {scheme.eligibility}
                    </p>

                </div>



                <div className="scheme-section">

                    <h2>
                        Documents Required
                    </h2>

                    <p>
                        {scheme.documents}
                    </p>

                </div>



                <div className="scheme-section">

                    <h2>
                        Application Process
                    </h2>

                    <p>
                        {scheme.application}
                    </p>

                </div>

            </div>

        </MainLayout>
    );
}

export default SchemeDetails;