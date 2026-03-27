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

### Author

Sanjana S