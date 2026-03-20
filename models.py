from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / company / student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="user", uselist=False)
    company = db.relationship("Company", backref="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    batch_year = db.Column(db.Integer, nullable=False)
    resume_filename = db.Column(db.String(255))

    applications = db.relationship("Application", backref="student", lazy=True)


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact_name = db.Column(db.String(120), nullable=False)
    hr_contact_email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(255))
    approval_status = db.Column(db.String(20), default="Pending")  # Pending / Approved / Rejected

    drives = db.relationship("PlacementDrive", backref="company", lazy=True)


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    min_cgpa = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.String(20), default="Pending"
    )  # Pending / Approved / Closed / Rejected

    applications = db.relationship("Application", backref="drive", lazy=True)


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(
        db.Integer, db.ForeignKey("placement_drives.id"), nullable=False
    )
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(20), default="Applied"
    )  # Applied / Shortlisted / Selected / Rejected

    __table_args__ = (
        db.UniqueConstraint(
            "student_id", "drive_id", name="uq_student_drive_application"
        ),
    )

class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), unique=True, nullable=False)

    company_name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    package = db.Column(db.Float)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="placements")
    application = db.relationship("Application", backref=db.backref("placement", uselist=False))
    
def seed_default_admin():
    """Create a default admin user if it does not exist."""
    admin_email = "admin@institute.edu"
    existing = User.query.filter_by(email=admin_email, role="admin").first()
    if existing:
        return

    admin = User(
        email=admin_email,
        role="admin",
        is_active=True,
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()

