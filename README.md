# Placement Portal Application

A role-based web application built using Flask to manage campus recruitment activities involving Admin, Companies, and Students.


## Features

### Admin (Placement Cell)

* Approve/reject company registrations
* Approve/reject placement drives
* View all students, companies, drives, and applications
* Search students and companies
* Deactivate (blacklist) users
* Dashboard with counts (students, companies, drives, applications)

### Company

* Register and create company profile
* Login only after admin approval
* Create, edit, and close placement drives
* View applications for their drives
* Shortlist / Select / Reject students

### Student

* Register and login
* Update profile and upload resume
* View approved placement drives
* Search drives by company / title / skills
* Apply to drives (duplicate applications prevented)
* Track application status

## Tech Stack

* **Backend:** Flask
* **Frontend:** HTML, CSS, Bootstrap, Jinja2
* **Database:** SQLite (created programmatically using SQLAlchemy)
* **Authentication:** Flask-Login

### Setup Instructions
* Clone the repository

```bash
git clone https://github.com/Sanjana272621/placement_portal.git
cd placement_portal
```

* Create virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

* Install dependencies

```bash
pip install flask flask_sqlalchemy flask_login
```

* Run the application

```bash
python app.py
```

* Open in browser

```bash
http://127.0.0.1:5000/
```

### Report
Detailed explanation of system design, database schema, and implementation.  
https://docs.google.com/document/d/1Fd5pvddSO78RtwDJQsBrbOlcf2MFoo-AJtVIQiu7h_Y/edit?usp=sharing

### Demo Video 
A 5 minute walkthrough demonstrating all features and internal working.  
https://drive.google.com/file/d/1s0HxYgOKgQdc3xBVVrK0FEVgWb2Zn58q/view?usp=sharing

### Author

Sanjana S