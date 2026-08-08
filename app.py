from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)