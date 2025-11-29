# Hospital Management App

Hospital Management System — allows admin/doctor/patient workflows: user management, doctor availability, appointment booking, basic treatment records.

Made by: SABOO RIDDESH RAJAN  
Roll no: 24f1001102
Subject: MAD 1 Project
Email: 24f1001102@ds.study.iitm.ac.in

## Core Technologies Used
- Flask : Core backend web framework
- SQLAlchemy : Object Relational Mapper for SQLite database
- Jinja2 : Template engine for rendering dynamic HTML pages
- Bootstrap 5 : Frontend styling and responsive design

## Features

### Doctor Dashboard
- View assigned appointments
- Mark appointments as **Completed** or **Cancelled**
- Add **Diagnosis and Prescription** for each appointment
- View **Patient Medical History**
- Provide and update **Availability Schedule (Next 7 Days)**

### Patient Dashboard
- View available departments and doctors in those departments
- Book appointments based on doctor availability
- View upcoming, completed, and cancelled appointments
- View treatment history and prescriptions
- Print appointment and prescription details

### Admin Module
- Add and manage departments
- Add doctors and assign them to departments
- View all doctors and patients 
- Blacklist or Delete users (patients or doctors)
- View upcoming appointments
- View patient history

## Database structure
- User (user_id, full_name, email, password (hashed), contact, role, is_active)
- Department (department_id, name, description)
- Doctor (doctor_id, user_id → User, department_id → Department, specialization, about)
- Patient (patient_id, user_id → User, dob, address, blood_group)
- Availability (availability_id, doctor_id → Doctor, date, start_time, end_time, status)
- Appointment (appointment_id, patient_id → Patient, doctor_id → Doctor, appointment_date, appointment_time, status, availability_id)
- Treatment (treatment_id, appointment_id → Appointment, diagnosis, prescription, datetime)


## How to Run the Project (Using Virtual Environment)

1. Make sure Python is installed:

    python3 --version

2.	Create a virtual environment:

    python3 -m venv venv

3.	Activate the virtual environment:

	•	On Windows:

            venv\Scripts\activate

	•	On Mac/Linux:

            source venv/bin/activate

4.	Install required dependencies:

    pip install -r requirements.txt

5.	Run the Flask application:

    python3 app.py

6.	Open the browser and go to:

    http://127.0.0.1:5000


