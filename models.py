import bcrypt
from extentions import db
from datetime import datetime

# 1 User -> 1 doctor 
# 1 User -> 1 patient
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(32))
    role = db.Column(db.Enum('admin', 'doctor', 'patient', name='user_roles'), nullable=False, server_default='patient')
    is_active = db.Column(db.Boolean, nullable=False, server_default='1')
    doctor = db.relationship('Doctor', backref='user', uselist=False)
    patient = db.relationship('Patient', backref='user', uselist=False)

    def __init__(self, full_name, email, password, contact=None, role='patient'):
        self.full_name = full_name
        self.email = email
        # store hashed password
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.contact = contact
        self.role = role
        self.is_active = True

    @classmethod
    def create_admin(cls, full_name, email, password, contact=None):
        return cls(full_name=full_name, email=email, password=password, contact=contact, role='admin')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
     
# 1 department -> many doctors 
class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

# 1 doctor -> many availabilities
# 1 doctor -> many appointments
class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    specialization = db.Column(db.String(120))
    about = db.Column(db.Text)

    availabilities = db.relationship('Availability', backref='doctor', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

# 1 patient -> many appointments
class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    dob = db.Column(db.Date)
    address = db.Column(db.String(200))
    blood_group = db.Column(db.String(3))

    appointments = db.relationship('Appointment', backref='patient', lazy=True)


class Availability(db.Model):
    __tablename__ = 'availabilities'
    availability_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('available', 'booked','completed','canceled' , name='availability_status'),
                       nullable=False, server_default='available')

# 1 appointment -> 1 treatment
class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('scheduled', 'completed', 'canceled', name='appointment_status'),
                       nullable=False, server_default='scheduled')
    availability_id = db.Column(db.Integer, db.ForeignKey('availabilities.availability_id'))
    treatment = db.relationship('Treatment', backref='appointment', uselist=False)


class Treatment(db.Model):
    __tablename__ = 'treatments'
    treatment_id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)