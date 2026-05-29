from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

from ml_model import predict_ghost_probability

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ghosted.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False)
    last_contact_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    notes = db.Column(db.Text)
    ghost_probability = db.Column(db.Float)  # ML estimate, 0..1


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def check_ghosting():
    result = None
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        location = request.form.get('location')
        application_date_str = request.form.get('application_date')
        last_contact_date_str = request.form.get('last_contact_date')

        try:
            application_date = datetime.strptime(application_date_str, '%Y-%m-%d')
            last_contact_date = (datetime.strptime(last_contact_date_str, '%Y-%m-%d')
                                 if last_contact_date_str else None)

            days_since_contact = (datetime.now() - (last_contact_date or application_date)).days

            # Rule-based status (kept from the original logic).
            if days_since_contact > 14:
                status = "Likely ghosted"
                message = f"It's been {days_since_contact} days since last contact. You may have been ghosted."
            elif days_since_contact > 7:
                status = "Follow up recommended"
                message = "Consider sending a follow-up email."
            else:
                status = "Active"
                message = "Application is still active. Keep waiting."

            # ML estimate of ghosting probability.
            prob = predict_ghost_probability(days_since_contact, had_contact=last_contact_date is not None)

            application = Application(
                company_name=company_name,
                location=location,
                application_date=application_date,
                last_contact_date=last_contact_date,
                status=status,
                notes=message,
                ghost_probability=prob,
            )
            db.session.add(application)
            db.session.commit()

            result = {
                'status': status,
                'message': message,
                'days': days_since_contact,
                'probability': round(prob * 100, 1) if prob is not None else None,
            }
        except (ValueError, TypeError):
            flash('Please enter valid dates', 'error')

    return render_template('check_ghosting.html', result=result)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_application(id):
    application = Application.query.get_or_404(id)
    try:
        db.session.delete(application)
        db.session.commit()
        flash('Application record deleted successfully', 'success')
    except Exception:
        flash('Error deleting application record', 'error')
        db.session.rollback()
    return redirect(url_for('view_applications'))


@app.route('/applications')
def view_applications():
    applications = Application.query.order_by(Application.application_date.desc()).all()
    return render_template('applications.html', applications=applications)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=True)
