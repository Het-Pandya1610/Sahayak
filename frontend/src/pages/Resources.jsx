import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import './css/Resources.css';

import MainLayout from '../layouts/MainLayout';

function Resources() {
    return (
        <div className="resources-page">

            <MainLayout>
            <motion.div
                className="resources-content"
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
                Trusted Government Resources
            </h1>
            <div className="resource-sections">
                <section className="resource-section">

                    <h2>
                        Official Government Platforms
                    </h2>

                    <ul className="resources-list">

                        <li>
                            <a
                                href="https://www.india.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                National Portal of India
                            </a>

                            <p>
                                Official gateway to
                                Indian government
                                departments, citizen
                                services, schemes,
                                and public resources.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://www.mygov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                MyGov India
                            </a>

                            <p>
                                Citizen engagement
                                platform for government
                                initiatives, campaigns,
                                and public participation.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://www.niti.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                NITI Aayog
                            </a>

                            <p>
                                Official policy think
                                tank of the Government
                                of India providing
                                development strategies,
                                reports, and initiatives.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://pgportal.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                CPGRAMS Public Grievance Portal
                            </a>

                            <p>
                                Centralized government
                                grievance redressal
                                platform for lodging
                                complaints and tracking
                                complaint status.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://services.india.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                National Government Services Portal
                            </a>

                            <p>
                                Access to various online
                                public services, forms,
                                certificates, and citizen
                                service applications.
                            </p>
                        </li>

                    </ul>

                </section>

                {/* ========================= */}
                {/* WELFARE & SCHEMES */}
                {/* ========================= */}

                <section className="resource-section">

                    <h2>
                        Welfare Schemes & Citizen Support
                    </h2>

                    <ul className="resources-list">

                        <li>
                            <a
                                href="https://www.india.gov.in/my-government/schemes"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Government Schemes Portal
                            </a>

                            <p>
                                Comprehensive directory
                                of welfare schemes and
                                financial assistance
                                programs offered by the
                                Government of India.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://scholarships.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                National Scholarship Portal
                            </a>

                            <p>
                                Official scholarship
                                application and management
                                platform for students
                                across India.
                            </p>
                        </li>

                        <li>
                            <a
                                href="https://pmjay.gov.in/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Ayushman Bharat PM-JAY
                            </a>

                            <p>
                                Healthcare assistance and
                                health insurance support
                                scheme for eligible
                                citizens and families.
                            </p>
                        </li>

                    </ul>

                </section>

                <section className="resource-section txt-sctn">
                    <h2 className='ogr-hdr'>
                        Official Government Resources
                    </h2>
                    <p className="resources-description ogr-desc">
                        Sahayak utilizes verified government
                        resources, official public service
                        portals, and authentic informational
                        platforms to ensure users receive
                        accurate, reliable, and up-to-date
                        guidance regarding government schemes,
                        public welfare initiatives, complaint
                        registration systems, healthcare
                        programs, education support, and
                        citizen services across India.
                    </p>

                    <p className="resources-description ogr-desc">
                        Our platform is designed to simplify
                        access to official information by
                        connecting users directly with trusted
                        government websites and digital
                        service portals. This helps reduce
                        misinformation, improves accessibility,
                        and enables citizens to efficiently
                        discover schemes, benefits, and
                        grievance support systems relevant to
                        their needs.
                    </p>
                </section>

                {/* ========================= */}
                {/* TRANSPARENCY */}
                {/* ========================= */}

                <section className="resource-section txt-sctn">

                    <h2>
                        Information Reliability
                    </h2>

                    <p className="resources-description trn-desc">
                        Sahayak does not generate
                        unofficial scheme data or
                        fabricate public information.
                        The platform is designed to
                        guide users using publicly
                        available government data,
                        verified portals, and trusted
                        digital services to ensure
                        transparency, reliability,
                        and accessibility.
                    </p>

                    <p className="resources-description trn-desc">
                        Users are always encouraged
                        to verify critical information
                        directly through official
                        government websites linked
                        above before submitting
                        applications or personal
                        information.
                    </p>

                </section>
            </div>
            </motion.div>

            </MainLayout>

        </div>
    );
}

export default Resources;