import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

import './css/Contact.css';
import MainLayout from '../layouts/MainLayout';


function Contact() {

    const [formData, setFormData] = useState({
        name: '',
        message: ''
    });


    const [status, setStatus] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);


    const handleChange = (e) => {

        const { name, value } = e.target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: value
        }));
    };


    const handleSubmit = async (e) => {

        e.preventDefault();

        setIsSubmitting(true);
        setStatus('');


        try {

            const token = localStorage.getItem('token');


            if (!token) {

                setStatus(
                    'Please login before contacting us.'
                );

                setIsSubmitting(false);
                return;
            }



            const response = await axios.post(
                'http://127.0.0.1:8000/api/contact/',
                {
                    name: formData.name,
                    message: formData.message
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );



            if (response.data.success) {

                setStatus(
                    'Your message has been sent successfully!'
                );


                setFormData({
                    name: '',
                    message: ''
                });
            }


        } catch (error) {


            console.error(
                'Contact form error:',
                error
            );


            if (error.response?.status === 401) {

                setStatus(
                    'Your session has expired. Please login again.'
                );

            } 
            else if (error.response?.data?.message) {

                setStatus(
                    error.response.data.message
                );

            } 
            else {

                setStatus(
                    'Something went wrong. Please try again later.'
                );
            }


        } finally {

            setIsSubmitting(false);

        }

    };



    return (

        <div className="contact-page">

            <MainLayout>


                <motion.div

                    className="contact-content"

                    initial={{
                        opacity: 0,
                        y: 20
                    }}

                    animate={{
                        opacity: 1,
                        y: 0
                    }}

                    transition={{
                        duration: 0.5,
                        ease: 'easeOut'
                    }}

                >


                    <h1>
                        Contact Us
                    </h1>



                    <p className="contact-description">

                        We would love to hear from you! Whether you have
                        questions, feedback, or just want to say hello,
                        feel free to reach out to us using the form below.

                    </p>




                    <form

                        className="contact-form"

                        onSubmit={handleSubmit}

                    >



                        <label htmlFor="name">
                            Name
                        </label>



                        <input

                            type="text"

                            id="name"

                            name="name"

                            placeholder="Your name.."

                            value={formData.name}

                            onChange={handleChange}

                            required

                        />





                        <label htmlFor="message">

                            Message

                        </label>




                        <textarea

                            id="message"

                            name="message"

                            placeholder="Write something.."

                            value={formData.message}

                            onChange={handleChange}

                            required

                            rows="6"

                        />





                        <button

                            type="submit"

                            disabled={isSubmitting}

                        >

                            {
                                isSubmitting
                                    ? 'Sending...'
                                    : 'Submit'
                            }

                        </button>



                    </form>





                    {
                        status && (

                            <p className="contact-status">

                                {status}

                            </p>

                        )
                    }






                    <p className="contact-info">

                        You can also reach us at:{' '}


                        <a href="mailto:teamsahayak3@gmail.com">

                            teamsahayak3@gmail.com

                        </a>


                    </p>




                </motion.div>



            </MainLayout>


        </div>

    );

}


export default Contact;