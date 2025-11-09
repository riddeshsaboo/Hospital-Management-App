from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
# from flask_sqlalchemy import SQLAlchemy
from extentions import db
from models import User

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

        if not name or not email or not password or not contact:
            flash('Please enter all the required fields', 'warning')
            return render_template('register.html')

        # if the email already exist in the db 
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return render_template('register.html')

        # create patient user only
        new_user = User(full_name=name, email=email, password=password, contact=contact) #user model ka constructor
        db.session.add(new_user)
        db.session.commit()

        flash('Account created. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

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
        return render_template('patient_dashboard.html', user=user)
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
        return render_template('admin_dashboard.html', user=user)
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



if __name__ == '__main__':
    # when app is run , creating admin if he does not exist 
    with app.app_context():
        existing_admin = User.query.filter_by(email="admin@gmail.com").first()
        if not existing_admin:
            admin_db = User.create_admin(full_name="Administrator", email="admin@gmail.com", password="admin@123", contact=None)
            db.session.add(admin_db)
            db.session.commit()

    app.run(debug=True)