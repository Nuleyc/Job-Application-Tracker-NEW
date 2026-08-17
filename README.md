Job Application Tracker
A full-stack web application for tracking job applications, built as my capstone project for the Software Development certificate at Bridgerland Technical College.

About
I built this tracker to solve my own problems with job hunting. It is a simple, organized way to log every application I submit, update its status as I hear back, and get automatic reminders to follow up if I haven't heard anything in a while.

Features
Add, edit, and delete job applications
Track status for each application (Applied, Interview, Offer, Rejected) with color-coded visual indicators
Optional fields for phone number and notes per application
Relational database — applications are linked to companies, so multiple applications to the same company stay organized without duplicate data
Automated email reminders — sends an email if an application has had no status update in 7+ days, so nothing falls through the cracks
Standalone desktop app — packaged into a Windows executable, no need to install Python, Flask, or run it from a terminal

Tech Stack
Layer	Technology
Backend	Python, Flask
Database	SQLite, SQLAlchemy (Flask-SQLAlchemy)
Frontend	HTML, CSS, Jinja2 templating
Email	Flask-Mail, Gmail SMTP
Scheduling	APScheduler
Packaging	PyInstaller
Version Control
<img width="634" height="928" alt="Screenshot 2026-08-16 213839" src="https://github.com/user-attachments/assets/0e41a6fc-25aa-4bd8-834a-0109bccebf24" />

Running the Project
Option 1: Run the desktop app (easiest)
Download app.exe from the Releases section of this repo (or wherever you host it)
Double-click app.exe
Your browser will open automatically to the app — no installation required
If i missed anything major please let me know

Database Schema
Company — id, name
Job — id, position, status, date_applied, phone_number, notes, company_id (foreign key → Company)

Author

Built by Nuley Cornia as a capstone project for the Software Development certificate at Bridgerland Technical College.
