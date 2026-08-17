from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import webbrowser
from threading import Timer

load_dotenv()

app = Flask(__name__)          # <-- app must be created FIRST

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"   # <-- your original DB config
db = SQLAlchemy(app)

# --- Database Models ---

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    jobs = db.relationship("Job", backref="company", lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    date_applied = db.Column(db.String(20))
    notes = db.Column(db.Text)
    phone_number = db.Column(db.String(20))  # NEW — optional, can be blank
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

def check_and_send_reminders():
    with app.app_context():
        cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        stale_jobs = Job.query.filter(
            Job.status == "Applied",
            Job.date_applied <= cutoff_date
        ).all()

        if stale_jobs:
            body_lines = ["The following applications haven't been updated in 7+ days:\n"]
            for job in stale_jobs:
                body_lines.append(f"- {job.company.name}: {job.position} (Applied {job.date_applied})")

            msg = Message(
                subject="Job Tracker: Follow-up Reminders",
                recipients=[os.getenv("MAIL_USERNAME")],
                body="\n".join(body_lines)
            )
            mail.send(msg)
            print(f"Sent reminder email for {len(stale_jobs)} application(s).")

# --- Routes ---

@app.route("/")
def home():
    jobs = Job.query.all()
    return render_template("index.html", jobs=jobs)

@app.route("/add", methods=["POST"])
def add_job():
    company_name = request.form["company_name"]
    position = request.form["position"]
    status = request.form["status"]
    date_applied = request.form["date_applied"]
    notes = request.form.get("notes", "")
    phone_number = request.form.get("phone_number", "")

    company = Company.query.filter_by(name=company_name).first()
    if not company:
        company = Company(name=company_name)
        db.session.add(company)
        db.session.commit()

    new_job = Job(
        position=position,
        status=status,
        date_applied=date_applied,
        notes=notes,
        phone_number=phone_number,
        company_id=company.id
    )
    db.session.add(new_job)
    db.session.commit()

    return redirect("/")


@app.route("/edit/<int:job_id>")
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("edit.html", job=job)


@app.route("/update/<int:job_id>", methods=["POST"])
def update_job(job_id):
    job = Job.query.get_or_404(job_id)

    company_name = request.form["company_name"]
    company = Company.query.filter_by(name=company_name).first()
    if not company:
        company = Company(name=company_name)
        db.session.add(company)
        db.session.commit()

    job.company_id = company.id
    job.position = request.form["position"]
    job.status = request.form["status"]
    job.date_applied = request.form["date_applied"]
    job.notes = request.form.get("notes", "")
    job.phone_number = request.form.get("phone_number", "")

    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:job_id>")
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect("/")

@app.route("/update_status/<int:job_id>", methods=["POST"])
def update_status(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = request.form["status"]
    db.session.commit()
    return redirect("/")

@app.route("/test_reminder")
def test_reminder():
    check_and_send_reminders()
    return "Reminder check triggered! Check your email (if any applications are 7+ days old with 'Applied' status)."

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_send_reminders, trigger="interval", hours=24)
    scheduler.start()
    Timer(1.5, open_browser).start()
    app.run(debug=False)