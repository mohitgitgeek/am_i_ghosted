from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ghosted.db'
db = SQLAlchemy(app)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False)
    last_contact_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    notes = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def check_ghosting():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        location = request.form.get('location')
        application_date_str = request.form.get('application_date')
        last_contact_date_str = request.form.get('last_contact_date')
        
        try:
            application_date = datetime.strptime(application_date_str, '%Y-%m-%d')
            last_contact_date = datetime.strptime(last_contact_date_str, '%Y-%m-%d') if last_contact_date_str else None
            
            # Calculate days since last contact
            days_since_contact = (datetime.now() - (last_contact_date or application_date)).days
            
            # Determine ghosting status
            if days_since_contact > 14:
                status = "Likely ghosted"
                message = f"It's been {days_since_contact} days since last contact. You may have been ghosted."
            elif days_since_contact > 7:
                status = "Follow up recommended"
                message = "Consider sending a follow-up email."
            else:
                status = "Active"
                message = "Application is still active. Keep waiting."
            
            # Save to database
            application = Application(
                company_name=company_name,
                location=location,
                application_date=application_date,
                last_contact_date=last_contact_date,
                status=status,
                notes=message
            )
            db.session.add(application)
            db.session.commit()
            
            flash(message, 'info')
            return redirect(url_for('view_applications'))
            
        except ValueError:
            flash('Please enter valid dates', 'error')
    
    return render_template('check_ghosting.html')

@app.route('/applications')
def view_applications():
    applications = Application.query.order_by(Application.application_date.desc()).all()
    return render_template('applications.html', applications=applications)

if __name__ == '__main__':
    app.run(debug=True)