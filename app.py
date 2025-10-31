from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  


db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('base.html')


# App run 
if __name__ == '__main__':
    with app.app_context():  
        db.create_all()      # Creating the database and tables
    app.run(debug=True)