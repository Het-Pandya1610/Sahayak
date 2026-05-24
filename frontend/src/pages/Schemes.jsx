import React, {
    useEffect,
    useState
} from 'react';

import './css/Schemes.css';
import MainLayout from '../layouts/MainLayout';
import { useNavigate } from 'react-router-dom';

function Schemes() {
    const navigate = useNavigate();
    const [schemes, setSchemes] = useState([]);

    const [loading, setLoading] = useState(true);

    const [page, setPage] = useState(1);

    const [totalPages, setTotalPages] = useState(1);

    const [search, setSearch] = useState('');

    const [category, setCategory] = useState('');

    useEffect(() => {

        fetchSchemes();

    }, [page, search, category]);



    const fetchSchemes = async () => {

        try {

            setLoading(true);

            const response = await fetch(

                `http://127.0.0.1:8000/api/schemes/?page=${page}&search=${search}&category=${category}`

            );

            const data = await response.json();

            setSchemes(
                data.schemes
            );

            setTotalPages(
                data.total_pages
            );

        }

        catch (error) {

            console.error(
                'API Error:',
                error
            );
        }

        finally {

            setLoading(false);
        }
    };



    return (

        <MainLayout>

            <div className="schemes-page">

                <h1>
                    Government Schemes
                </h1>

                {/* SEARCH */}
                <div className="scheme-search-filter">
                    <input
                        type="text"
                        placeholder="Search schemes..."
                        value={search}
                        onChange={(e) => {

                            setPage(1);

                            setSearch(
                                e.target.value
                            );

                        }}
                    />



                    {/* FILTER */}

                    <select
                        value={category}
                        onChange={(e) => {

                            setPage(1);

                            setCategory(
                                e.target.value
                            );

                        }}
                    >

                        <option value="">
                            All Categories
                        </option>

                        <option value="Health">
                            Health
                        </option>

                        <option value="Agriculture">
                            Agriculture
                        </option>

                        <option value="Education">
                            Education
                        </option>

                        <option value="Employment">
                            Employment
                        </option>

                        <option value="Housing">
                            Housing
                        </option>

                        <option value="Social Welfare">
                            Social Welfare
                        </option>

                        <option value="Technology">
                            Technology
                        </option>

                        <option value="Environment">
                            Environment
                        </option>

                        <option value="Business">
                            Business
                        </option>
                    </select>
                </div>


                {/* LOADING */}

                {

                    loading

                    ?

                    <p className="loading-text">
                        Loading schemes...
                    </p>

                    :

                    <div className="schemes-grid">

                        {

                            schemes.map(

                                scheme => (

                                    <div
                                        key={scheme.id}
                                        className="scheme-card"
                                        onClick={() => {
                                            navigate(`/schemes/${scheme.id}`);
                                        }}
                                    >

                                        <h3>
                                            {
                                                scheme.scheme_name
                                            }
                                        </h3>

                                        <p>
                                            {
                                                scheme.details?.slice(
                                                    0,
                                                    150
                                                )
                                            }...
                                        </p>

                                        <span>
                                            {
                                                scheme.schemeCategory
                                            }
                                        </span>

                                    </div>
                                )
                            )
                        }

                    </div>
                }



                {/* PAGINATION */}

                <div className="pagination">

                    <button
                        disabled={
                            page === 1
                        }
                        onClick={() =>
                            setPage(
                                page - 1
                            )
                        }
                    >
                        Prev
                    </button>

                    <span>

                        Page {page}
                        {' / '}
                        {totalPages}

                    </span>

                    <button
                        disabled={
                            page === totalPages
                        }
                        onClick={() =>
                            setPage(
                                page + 1
                            )
                        }
                    >
                        Next
                    </button>

                </div>

            </div>

        </MainLayout>
    );
}

export default Schemes;