from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
# from flask_sqlalchemy import SQLAlchemy
from extentions import db
from models import Appointment, Availability, Treatment, User,Doctor,Department,Patient
from datetime import date , datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'riddesh_s')  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  



# initialise
db.init_app(app)

with app.app_context():
    db.create_all()  # creating the tables of db
    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('email'):
        return redirect(url_for('patient_dashboard'))
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        contact = (request.form.get('contact') or '').strip()
        dob_str = request.form.get('dob') 
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() 
        blood_group = request.form.get('blood_group')
        address = request.form.get('address')

        if not name or not email or not password or not contact and not dob or not blood_group :
            flash('Please enter all the required fields', 'warning')
            return render_template('register.html',current_date=date.today())

        # if the email already exist in the db 
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return render_template('register.html',current_date=date.today())

        # create patient user only
        new_user = User(full_name=name, email=email, password=password, contact=contact) #user model ka constructor
        new_patient = Patient(user=new_user, dob=dob, blood_group=blood_group, address=address)  
        db.session.add(new_user)
        db.session.add(new_patient)
        db.session.commit()

        flash('Account created. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', current_date=date.today())

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active and user.role == 'patient':
            session['email'] = user.email
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['full_name'] = user.full_name
            
            return redirect('/patient_dashboard')
        elif user and user.check_password(password) and user.is_active and user.role == 'admin':
            session['email'] = user.email
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['full_name'] = user.full_name
            return redirect('/admin_dashboard')
        elif user and user.check_password(password) and user.is_active and user.role == 'doctor':
            session['email'] = user.email
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['full_name'] = user.full_name
            return redirect('/doctor_dashboard')
        elif user and not user.is_active:
            return render_template('login.html',error='Account is inactive.Please contact the admin.')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/patient_dashboard')
def patient_dashboard():
    if session.get('role') != 'patient': # if say doctor or admin tries to access this patient dashboard then 
            if session.get('role') == 'admin': # if he is admin 
                return redirect('/admin_dashboard')
            elif session.get('role') == 'doctor': # if he is doctor 
                return redirect('/doctor_dashboard')
            else : # if he is not logged in
                return redirect('/logout')
    if session.get('email'):
        user = User.query.filter_by(email=session.get('email')).first()
        departments = Department.query.all()
        scheduled_appointments = (db.session.query(Appointment, Doctor, Patient, User).join(Doctor, Appointment.doctor_id == Doctor.doctor_id).join(Patient, Appointment.patient_id == Patient.patient_id).join(User, Patient.user_id == User.user_id).filter(Patient.user_id == user.user_id , Appointment.status == 'scheduled' , Appointment.appointment_date >= date.today()).all())
        completed_appointments = (db.session.query(Appointment, Doctor, Patient, User).join(Doctor, Appointment.doctor_id == Doctor.doctor_id).join(Patient, Appointment.patient_id == Patient.patient_id).join(User, Patient.user_id == User.user_id).filter(Patient.user_id == user.user_id , Appointment.status == 'completed').all())
        cancelled_appointments = (db.session.query(Appointment, Doctor, Patient, User).join(Doctor, Appointment.doctor_id == Doctor.doctor_id).join(Patient, Appointment.patient_id == Patient.patient_id).join(User, Patient.user_id == User.user_id).filter(Patient.user_id == user.user_id , Appointment.status == 'canceled').all())
        total_departments = len(departments)
        total_scheduled_appointments = len(scheduled_appointments)
        total_completed_appointments = len(completed_appointments)
        total_cancelled_appointments = len(cancelled_appointments)

        return render_template('patient_dashboard.html', user=user, departments=departments , scheduled_appointments=scheduled_appointments , total_departments = total_departments , total_scheduled_appointments = total_scheduled_appointments , completed_appointments=completed_appointments , cancelled_appointments=cancelled_appointments , total_completed_appointments=total_completed_appointments , total_cancelled_appointments=total_cancelled_appointments ) 
    return redirect('/login') # if he is not logged in


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
            if session.get('role') == 'patient':
                return redirect('/patient_dashboard')
            elif session.get('role') == 'doctor':
                return redirect('/doctor_dashboard')
            else : 
                return redirect('/logout')
    if session.get('email'):
        user = User.query.filter_by(email=session.get('email')).first()
        doctors = (db.session.query(Doctor, User).join(User, Doctor.user_id == User.user_id).all())
        patients = (db.session.query(Patient, User).join(User, Patient.user_id == User.user_id).all())
        appointments_count = sum(len(doctor.appointments) for doctor, user in doctors)
        total_doctors = len(doctors)
        total_patients = len(patients)  
        return render_template('admin_dashboard.html', user=user, doctors=doctors, patients=patients, total_doctors=total_doctors, total_patients=total_patients, total_appointments=appointments_count)
    return redirect('/login')

@app.route('/doctor_dashboard')
def doctor_dashboard(): 
    if session.get('email'):
        if session.get('role') != 'doctor':
            if session.get('role') == 'admin':
                return redirect('/admin_dashboard')
            elif session.get('role') == 'patient':
                return redirect('/patient_dashboard')
            else : 
                return redirect('/logout')
        user = User.query.filter_by(email=session.get('email')).first()
        return render_template('doctor_dashboard.html', user=user)
    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



@app.route('/admin_dashboard/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        departments = Department.query.all()
        total_departments = len(departments)
        return render_template('add_doctor.html', departments=departments, total_departments=total_departments)
    if request.method == 'POST':
        try:
            doctor_name = request.form.get('doctor_name')
            email = request.form.get('email')
            password = request.form.get('password')
            contact = request.form.get('contact')
            specialization = request.form.get('specialization')
            department_id = request.form.get('department_id')
            about = request.form.get('about', '')

            # Validate required fields
            if not all([doctor_name, email, password, specialization, department_id]):
                flash("All fields are required.", "danger")
                return redirect(url_for('admin_dashboard'))

            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("A user with this email already exists.", "warning")
                return redirect(url_for('admin_dashboard'))

            new_user = User(
                    full_name=doctor_name,
                    email=email,
                    password=password,
                    contact=contact,
                    role='doctor'
                )
            db.session.add(new_user)
            db.session.flush()  # get user_id before commit

            # Now create Doctor record linked to that user_id
            new_doctor = Doctor(
                user_id=new_user.user_id,
                department_id=int(department_id),
                specialization=specialization,
                about=about
            )

            db.session.add(new_doctor)
            db.session.commit()

            flash(f"Doctor '{doctor_name}' added successfully!", "success")   
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")
            print(str(e))   

        return redirect(url_for('admin_dashboard')) 


@app.route('/search_doctor', methods=['GET'])
def search_doctor():
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    query = (request.args.get('query') or '').strip()
    if not query:
        return redirect(url_for('view_doctors'))

    results = (
        db.session.query(Doctor, User)
        .join(User, Doctor.user_id == User.user_id)
        .outerjoin(Department, Doctor.department_id == Department.department_id)
        .filter(
            (User.full_name.ilike(f"%{query}%")) |
            (Doctor.specialization.ilike(f"%{query}%")) |
            (Department.name.ilike(f"%{query}%"))
        )
        .all()
    )

    total_results = len(results)
    if not results:
        flash("No doctors found.", "warning")

    return render_template('view_doctors.html', doctors=results, total_doctors=total_results)

@app.route('/search_patient', methods=['GET'])
def search_patient():
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    query = request.args.get('query', '').strip()

    if not query:
        return redirect(url_for('view_patients'))

    results = (
        db.session.query(Patient, User)
        .join(User, Patient.user_id == User.user_id)
        .filter(
            (User.full_name.ilike(f"%{query}%")) |
            (User.contact.ilike(f"%{query}%"))
        )
        .all()
    )

    total_results = len(results)

    if not results:
        flash("No patients found.", "warning")

    return render_template(
        'view_patients.html',
        user=User.query.filter_by(email=session.get('email')).first(),
        patients=results , total_patients=total_results
    )

@app.route('/admin_dashboard/add_department', methods=['GET', 'POST'])
def add_department(): 
    if request.method == 'GET':
        return render_template('add_department.html')
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        existing_department = Department.query.filter_by(name=name).first()
        if existing_department:
            flash("A department with this name already exists.", "danger")
            return redirect(url_for('add_department'))

        new_department = Department(name=name, description=description)
        db.session.add(new_department)
        db.session.commit()

        flash(f"Department '{name}' added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    


@app.route('/admin_dashboard/view_doctors', methods=['GET'])
def view_doctors():
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    doctors = (db.session.query(Doctor, User).join(User, Doctor.user_id == User.user_id).all())
    total_doctors = len(doctors)
    return render_template('view_doctors.html' ,doctors=doctors, total_doctors=total_doctors)


@app.route('/admin_dashboard/view_departments',methods = ['GET'])
def view_departments() :
    if session.get('role') != 'admin':
        flash('Unauthorised access.','danger')
        return redirect(url_for('login'))
    
    departments = Department.query.all()
    total_departments = len(departments)

    return render_template('view_departments.html',departments=departments, total_departments=total_departments)

@app.route('/admin_dashboard/departmentwise_doctors/<int:department_id>', methods=['GET'])
def departmentwise_doctors(department_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    department = Department.query.get(department_id)
    if not department:
        flash("Department not found.", "danger")
        return redirect(url_for('view_departments'))

    doctors = (db.session.query(Doctor, User)
               .join(User, Doctor.user_id == User.user_id)
               .filter(Doctor.department_id == department_id)
               .all())
    total_doctors = len(doctors)

    return render_template('departmentwise_doctors.html', department=department, doctors=doctors, total_doctors=total_doctors)


@app.route('/blacklist_user/<int:user_id>', methods=['POST'])
def blacklist_user(user_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        
        user.is_active = False
        db.session.commit()

        flash(f"User '{user.full_name}' has been deactivated.", "success")

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        print(str(e))

    return redirect(url_for('admin_dashboard'))

@app.route('/unblacklist_user/<int:user_id>', methods=['POST'])
def unblacklist_user(user_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        user.is_active = True
        db.session.commit()
        flash(f"User '{user.full_name}' has been activated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        print(str(e))

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try :
        if session.get('role') != 'admin':
            flash("Unauthorized access.", "danger")
            return redirect(url_for('login'))
        
        user = User.query.get(user_id)
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('admin_dashboard'))

        if user.role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            if doctor:
                # Deleting availabilities and appointments of that doctor and then delete from doctor table 
                Availability.query.filter_by(doctor_id=doctor.doctor_id).delete()
                Appointment.query.filter_by(doctor_id=doctor.doctor_id).delete()
                db.session.delete(doctor)
        elif user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.user_id).first()
            if patient:
                # Delete associated appointments of that patient and then delete from patient table
                Appointment.query.filter_by(patient_id=patient.patient_id).delete()
                db.session.delete(patient)
        
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.full_name}' has been deleted.", "success")

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        # print(str(e))

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/view_patients', methods=['GET'])
def view_patients(): 
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    patients = (db.session.query(Patient, User).join(User, Patient.user_id == User.user_id).all())
    total_patients = len(patients)
    return render_template('view_patients.html', patients=patients, total_patients=total_patients)

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        user.full_name = request.form.get('name')
        user.email = request.form.get('email')
        user.contact = request.form.get('contact')

        if user.role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            doctor.specialization = request.form.get('specialization')
            doctor.about = request.form.get('about')

        elif user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.user_id).first()
            patient.dob = request.form.get('dob') 
            patient.blood_group = request.form.get('blood_group')
            patient.address = request.form.get('address')

        db.session.commit()
        flash(f"User '{user.full_name}' has been updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        print(str(e))

    return redirect(url_for('admin_dashboard'))


@app.route('/view_appointments' , methods=['GET'])
def view_appointments():
    if session.get('role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    
    appointments = []
    doctors = Doctor.query.all()
    for doctor in doctors:
        for appointment in doctor.appointments:
            patient_user = User.query.join(Patient).filter(Patient.patient_id == appointment.patient_id).first()
            appointments.append((appointment, doctor, patient_user))

    total_appointments = len(appointments)

    return render_template('view_appointments.html', appointments=appointments , total_appointments=total_appointments)

@app.route('/patient_dashboard/department_details', methods=['GET'])
def department_details():
    if session.get('role') != 'patient':
            if session.get('role') == 'admin':
                return redirect('/admin_dashboard')
            elif session.get('role') == 'doctor':
                return redirect('/doctor_dashboard')
            else : 
                return redirect('/logout')
    department_id = request.args.get('department_id')
    department = Department.query.get(department_id)
    if not department:
        flash("Department not found.", "danger")
        return redirect(url_for('patient_dashboard'))

    doctors = (db.session.query(Doctor, User)
               .join(User, Doctor.user_id == User.user_id)
               .filter(Doctor.department_id == department_id)
               .all())
    total_doctors = len(doctors)

    return render_template('department_details.html', department=department, doctors=doctors, total_doctors=total_doctors)

@app.route('/patient_dashboard/doctor_availability', methods=['GET'])
def doctor_availability():
    if session.get('role') != 'patient':
            if session.get('role') == 'admin':
                return redirect('/admin_dashboard')
            elif session.get('role') == 'doctor':
                return redirect('/doctor_dashboard')
            else : 
                return redirect('/logout')
    doctor_id = request.args.get('doctor_id')
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for('patient_dashboard'))

    availabilities = Availability.query.filter_by(doctor_id=doctor_id).all()
    total_slots = len(availabilities)

    current_date = date.today()
    current_time = datetime.now().time()

    return render_template('doctor_availability.html', doctor=doctor, availabilities=availabilities, total_slots=total_slots,current_date=current_date,current_time=current_time)


# yaaha se continue ....
@app.route('/patient_dashboard/book_appointment', methods=['POST'])
def book_appointment():
    # print(-1)
    
    if session.get('role') != 'patient':
        flash("You must be logged in as a patient to book an appointment.", "danger")
        return redirect(url_for('login'))

    availability_id = request.form.get('availability_id')
    if not availability_id:
        flash("No time slot selected.", "danger")
        # print(0)
        return redirect(url_for('patient_dashboard'))

    availability = Availability.query.get(availability_id)
    if not availability:
        flash("Selected time slot not found.", "danger")
        # print(1)
        return redirect(url_for('patient_dashboard'))

    # patient = Patient.query.filter_by(user_id=session.get('user_id')).first()
    
    patient = Patient.query.filter_by(user_id = session.get('user_id')).first() 
    user = User.query.filter_by(user_id = session.get('user_id')).first()
    print(session.get('user_id'),user.role)
    if not patient:
        flash("Patient record not found for current user.", "danger")
        # print(2)
        return redirect(url_for('patient_dashboard'))

    try:
        new_appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=availability.doctor_id,
            appointment_date=availability.date,
            appointment_time=availability.start_time,   
            status='scheduled'
        )

        db.session.add(new_appointment)
        db.session.delete(availability)  # remove the slot once booked
        db.session.commit()

        flash("Appointment booked successfully!", "success")
    except Exception as e:
        print(6)
        db.session.rollback()
        flash("Could not book appointment: " + str(e), "danger")
        app.logger.exception("book_appointment error")

    return redirect(url_for('patient_dashboard'))
    

@app.route('/patient_dashboard/cancel_appointment/', methods=['POST'])
def cancel_appointment(): 
    if request.method != 'POST':
        return redirect(url_for('patient_dashboard'))
    if session.get('role') != 'patient':
        flash("You must be logged in as a patient to cancel an appointment.", "danger")
        return redirect(url_for('login'))
   
    appointment_id = request.form.get('appointment_id')
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for('patient_dashboard'))   
    try:
        appointment.status = 'canceled'
        db.session.commit()
        flash("Appointment canceled successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Could not cancel appointment: " + str(e), "danger")

    return redirect(url_for('patient_dashboard'))

@app.route('/patient_dashboard/appointment_details/', methods=['POST'])
def view_appointment_details():
    if session.get('role') != 'patient':
        flash("You must be logged in as a patient to view appointment details.", "danger")
        return redirect(url_for('login'))
    
    appointment_id = request.args.get('appointment_id')
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash("Appointment details not found.", "danger")
        return redirect(url_for('patient_dashboard'))

    doctor = Doctor.query.get(appointment.doctor_id)
    patient = Patient.query.get(appointment.patient_id)
    treatment = Treatment.query.filter_by(appointment_id=appointment.appointment_id).first()

    return render_template('appointment_details.html', appointment=appointment, doctor=doctor, patient=patient, treatment=treatment)



# Just for testing purpose
def insert_dummy_slot(doctor_id: int | None = None):
    with app.app_context():
        # pick a doctor
        doctor = None
        if doctor_id:
            doctor = Doctor.query.get(doctor_id)
        if not doctor:
            doctor = Doctor.query.first()
        if not doctor:
            print("No doctor found. Create a doctor first (via admin).")
            return

        slot_date = date.today() + timedelta(days=1)          # tomorrow
        # start = time(10, 0)                                   # 10:00 AM
        # end = time(10, 30)                                    # 10:30 AM
        # create time objects using datetime.strptime().time()
        start = datetime.strptime("10:00", "%H:%M").time()    # 10:00 AM
        end = datetime.strptime("10:30", "%H:%M").time()      # 10:30 AM

        # ensure no duplicate
        existing = Availability.query.filter_by(
            doctor_id=doctor.doctor_id, date=slot_date, start_time=start, end_time=end
        ).first()
        if existing:
            print("Slot already exists:", existing.availability_id)
            return

        a = Availability(
            doctor_id=doctor.doctor_id,
            date=slot_date,
            start_time=start,
            end_time=end
        )
        db.session.add(a)
        db.session.commit()
        print("Inserted dummy slot for doctor_id", doctor.doctor_id, "on", slot_date)


if __name__ == '__main__':
    # when app is run , creating admin if he does not exist 
    with app.app_context():
        existing_admin = User.query.filter_by(email="admin@gmail.com").first()
        if not existing_admin:
            admin_db = User.create_admin(full_name="Administrator", email="admin@gmail.com", password="admin@123", contact=None)

            db.session.add(admin_db)
            db.session.commit()

    insert_dummy_slot(doctor_id=None)

    app.run(debug=True, host="0.0.0.0", port=5000)