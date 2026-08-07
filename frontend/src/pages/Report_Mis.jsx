import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

import './css/Report_Mis.css';
import MainLayout from '../layouts/MainLayout';


function Report_Mis() {


    const [formData, setFormData] = useState({

        url: '',
        description: ''

    });


    const [status, setStatus] = useState('');



    const handleChange = (e) => {

        setFormData({

            ...formData,

            [e.target.name]: e.target.value

        });

    };



    const handleSubmit = async (e) => {

        e.preventDefault();


        try {


            const token =
                localStorage.getItem('token');



            if(!token){

                setStatus(
                    "Please login before submitting a report."
                );

                return;

            }



            const response = await axios.post(

                'http://127.0.0.1:8000/api/contact/report-misinformation/',

                formData,

                {

                    headers: {

                        Authorization:
                        `Bearer ${token}`,

                        'Content-Type':
                        'application/json'

                    }

                }

            );



            if(response.data.success){

                setStatus(
                    "Report submitted successfully!"
                );


                setFormData({

                    url:'',
                    description:''

                });

            }



        }
        catch(error){

            console.log(error);

            setStatus(
                "Failed to submit report."
            );

        }

    };




    return (

        <div className="report-miss-page">

            <MainLayout>

                <motion.div

                    className="report-miss-content"

                    initial={{
                        opacity:0,
                        y:40
                    }}

                    animate={{
                        opacity:1,
                        y:0
                    }}

                    transition={{
                        duration:0.6
                    }}

                >

                    <h1>
                        Report Misinformation
                    </h1>


                    <p style={{
                        textAlign:'center',
                        margin:'auto'
                    }}>

                        If you come across any misinformation
                        on our website, please report it to us.

                    </p>



                    <form

                        className="report-form"

                        onSubmit={handleSubmit}

                    >


                        <label>
                            URL of the Misinformation:
                        </label>


                        <input

                            type="text"

                            name="url"

                            value={formData.url}

                            onChange={handleChange}

                            placeholder="Enter URL"

                            required

                        />



                        <label>
                            Description:
                        </label>


                        <textarea

                            name="description"

                            value={formData.description}

                            onChange={handleChange}

                            placeholder="Describe the issue"

                            required

                        />



                        <button type="submit">

                            Submit Report

                        </button>


                    </form>



                    {
                        status &&
                        <p>
                            {status}
                        </p>
                    }



                </motion.div>


            </MainLayout>


        </div>

    );

}


export default Report_Mis;