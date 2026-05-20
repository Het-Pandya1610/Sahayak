# Sahayak

Sahayak is an AI-powered citizen assistance chatbot designed to simplify common day-to-day issues faced by Indian citizens. It provides guided support for government services, municipal complaints, and welfare schemes through an interactive chatbot interface.

This project is being developed as a **45-day MVP by a 2-person team** for a college project, with a roadmap for future startup-scale expansion.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Detailed User Flows](#detailed-user-flows)
- [AI / ML Architecture](#ai--ml-architecture)
- [Database Design](#database-design)
- [Authentication & Security](#authentication--security)
- [API Architecture](#api-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Project Roadmap](#project-roadmap)
- [Team Execution Plan](#team-execution-plan)
- [Future Scope](#future-scope)

---

# Project Overview

Sahayak is a web-based AI chatbot that helps citizens with:

- Government service guidance
- Municipal complaint automation
- Welfare scheme guidance

The chatbot acts as a guided citizen assistant by combining:

- Database-driven FAQ responses
- Hosted LLM APIs
- Complaint automation workflows
- Complaint verification using computer vision
- Secure user authentication
- Email complaint generation and delivery

---

# Problem Statement

Indian citizens often face difficulties in:

- Understanding government processes
- Filing civic complaints
- Finding the correct authority contact
- Discovering eligible welfare schemes
- Navigating complex public service systems

These issues often result in:

- Delays
- Misdirected complaints
- Lack of awareness
- Citizen frustration

---

# Solution Overview

Sahayak solves this through a chatbot-based web application that provides:

1. Guided government service assistance
2. Complaint generation and delivery automation
3. Welfare scheme guidance
4. Authority lookup
5. AI-assisted complaint verification
6. Complaint escalation assistance

---

# Core Features

## 1. Government Services

Supports guidance for services such as:

- Aadhaar
- PAN Card
- Passport
- Voter ID
- Other government services

### Features

- Service selection interface
- Pre-stored FAQ cards
- Chat-based follow-up questions
- Hosted LLM API for custom guidance
- Step-by-step assistance

---

## 2. Municipal Complaints

Supports complaint categories such as:

- Potholes
- Garbage issues
- Drainage blockages

### Features

- Complaint category selection
- Location-based authority lookup
- Optional photo upload
- Complaint draft generation
- Complaint preview and editing
- PDF complaint generation
- Gmail-based complaint delivery
- Complaint status tracking
- Escalation complaint generation

---

## 3. Government Schemes

### Features

- State-based scheme filtering
- Scheme listing
- Scheme details
- Eligibility explanation
- Benefits explanation
- Chat-based follow-up guidance

---

# System Architecture

```text
Frontend (React + Tailwind)
        |
        v
REST API Layer
        |
        +----------------------+
        |                      |
        v                      v
Django Backend         FastAPI AI Services
        |                      |
        |                      +----------------+
        |                      |                |
        v                      v                v
MongoDB Atlas         LLM APIs        ResNet50 Model
        |
        v
Cloudinary / CSV / PDF / Email Services
```

---

# Tech Stack

## Frontend

- React
- Tailwind CSS
- React Context API
- Vercel

## Backend

### Main Backend

- Django

### AI Microservices

- FastAPI

## Database

- MongoDB Atlas

## Authentication

- Google OAuth
- Email + Password
- OTP
- JWT

## File Handling

- Cloudinary

## AI / ML

- Hosted LLM API
- ResNet50 (image verification)

## Deployment

- Docker
- Vercel
- MongoDB Atlas

---

# Detailed User Flows

---

## Government Services Flow

### Step 1

User selects:

- Aadhaar
- Passport
- PAN
- Voter ID
- etc.

### Step 2

System displays:

- FAQ cards
- Chat interface

### Step 3

User can:

- Click FAQ
- Ask custom question

### Step 4

Backend flow:

```text
User Question
    |
    v
Check FAQ DB
    |
    +------ FAQ Match ------> Return FAQ
    |
    +------ Custom Query --> Send to LLM API
                               |
                               v
                         Stream response
```

---

## Municipal Complaint Flow

### Step 1

User selects issue:

- Pothole
- Garbage
- Drainage

### Step 2

User provides:

- Location (mandatory)
- Photo (optional)

### Step 3

System:

- Finds nearest authority
- Verifies image (if uploaded)

### Step 4

Complaint draft generated

### Step 5

User:

- Reviews complaint
- Edits complaint
- Confirms complaint

### Step 6

System:

- Generates PDF
- Sends email using Gmail
- Stores complaint status

---

## Government Schemes Flow

### Step 1

User selects state

### Step 2

System displays schemes

### Step 3

User selects scheme

### Step 4

System shows:

- Eligibility
- Benefits
- Application process

### Step 5

User asks follow-up questions

---

# AI / ML Architecture

## Hosted LLM API

Used for:

- Government services guidance
- Welfare scheme assistance
- Dynamic question answering

---

## Complaint Image Verification

### Model

ResNet50 (pretrained + fine-tuned)

### Classes

- Pothole
- Garbage
- Drainage

### Flow

```text
User selects issue
       |
       v
Optional image uploaded
       |
       v
ResNet50 predicts class
       |
       +------ Match ------> Proceed
       |
       +------ Mismatch ---> Ask user to confirm
```

---

# Database Design

## Collections

---

### users

```json
{
  "name": "",
  "email": "",
  "phone": "",
  "address": "",
  "authProvider": "",
  "createdAt": ""
}
```

---

### faqs

```json
{
  "category": "",
  "service": "",
  "question": "",
  "answer": ""
}
```

---

### schemes

```json
{
  "state": "",
  "schemeName": "",
  "eligibility": "",
  "benefits": "",
  "applicationProcess": ""
}
```

---

### complaints

```json
{
  "userId": "",
  "issueType": "",
  "location": "",
  "authority": "",
  "complaintText": "",
  "pdfUrl": "",
  "status": ""
}
```

---

### chat_sessions

```json
{
  "userId": "",
  "messages": []
}
```

Stores only recent **4–5 messages**.

---

# Authority Data Structure

Authority lookup is handled using CSV data.

Example structure:

| State | City | Region | Authority Name | Email | Phone | Address |
|------|------|------|------|------|------|------|

---

# Authentication & Security

## Authentication Methods

- Google OAuth
- Email + Password
- OTP

## Security Features

- Password hashing
- JWT authentication
- OAuth token handling
- Encrypted sensitive data
- Private file access
- Secure API key management
- Encrypted uploads

---

# API Architecture

## Authentication

```http
POST /register
POST /login
POST /google-login
POST /verify-otp
```

---

## Government Services

```http
GET /services
GET /faq/:service
POST /ask-service
```

---

## Complaints

```http
GET /complaint-categories
POST /upload-evidence
POST /generate-complaint
POST /send-complaint
GET /complaint-status/:id
```

---

## Schemes

```http
GET /states
GET /schemes/:state
GET /scheme/:id
POST /ask-scheme
```

---

# Deployment Architecture

## Frontend

- Hosted on Vercel

## Backend

- Docker containers

## Database

- MongoDB Atlas

## AI Service

- FastAPI container

## File Storage

- Cloudinary

---

# Project Roadmap

## Week 1

- Project setup
- UI wireframes
- DB design
- Auth planning

## Week 2

- Login system
- Chatbot shell
- MongoDB integration

## Week 3

- Government services module
- FAQ flow
- LLM integration

## Week 4

- Complaint flow
- CSV authority lookup
- Complaint template generation

## Week 5

- File upload
- Cloudinary
- PDF generation
- Gmail sending

## Week 6

- Schemes module
- Testing
- Deployment
- Final polishing

---

# Team Execution Plan

## Developer 1

Responsible for:

- Frontend
- UI/UX
- React components
- Auth screens
- Chatbot rendering
- API integration

---

## Developer 2

Responsible for:

- Django backend
- FastAPI AI services
- MongoDB integration
- Complaint flow
- PDF generation
- Email delivery
- Model integration

---

# Risks & Fallback Strategy

| Risk | Fallback |
|------|------|
| Gmail OAuth complexity | Use system email for demo |
| AI dataset issues | Use issue selection only |
| LLM cost issues | Use smaller hosted model |
| Streaming issues | Use normal request-response |
| CNN deployment issues | Skip image verification in MVP |

---

# Future Scope

## Short Term (7–8 Months)

- Multi-language support
- More complaint categories
- Better image models
- Authority dashboards
- Complaint analytics

## Long Term

- Government integrations
- Full complaint lifecycle tracking
- Mobile app
- Startup-scale infrastructure
- Production-grade AI assistant

---

# MVP Scope (45 Days)

The MVP will focus on:

- Secure login
- Chatbot UI
- Government services FAQ + AI guidance
- Complaint generation
- PDF complaint creation
- Gmail complaint delivery
- Welfare scheme guidance
- Basic AI image verification
- MongoDB integration
- Deployment

---

# License

This project is currently developed as a college project prototype and startup-ready MVP.

Future licensing and deployment policies can be defined during production-scale development.

---

# Developers 

Het Pandya
Kavy Sachaniya
