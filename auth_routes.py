import os
from werkzeug.utils import secure_filename
from flask import current_app

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, Student, Company

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        if not user.is_active:
            flash("Your account is deactivated.", "danger")
            return render_template("login.html")

        if user.role == "company":
            company = Company.query.get(user.id)
            if not company:
                flash("Company profile not found.", "danger")
                return render_template("login.html")

            if company.approval_status != "Approved":
                flash("Your company account is pending admin approval.", "warning")
                return render_template("login.html")

        login_user(user)
        flash("Login successful.", "success")
        return redirect_by_role(user)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        roll_no = request.form.get("roll_no", "").strip()
        phone = request.form.get("phone", "").strip()
        department = request.form.get("department", "").strip()
        cgpa = request.form.get("cgpa", "").strip()
        batch_year = request.form.get("batch_year", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("register_student.html")

        if Student.query.filter_by(roll_no=roll_no).first():
            flash("Roll number already exists.", "danger")
            return render_template("register_student.html")

        resume_filename = None
        resume = request.files.get("resume")
        if resume and resume.filename:
            filename = secure_filename(resume.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "resumes")
            os.makedirs(upload_folder, exist_ok=True)
            resume.save(os.path.join(upload_folder, filename))
            resume_filename = filename

        user = User(email=email, role="student", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            id=user.id,
            name=name,
            roll_no=roll_no,
            phone=phone,
            department=department,
            cgpa=float(cgpa),
            batch_year=int(batch_year),
            resume_filename=resume_filename,
        )
        db.session.add(student)
        db.session.commit()

        flash("Student registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_student.html")

@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        hr_contact_name = request.form.get("hr_contact_name", "").strip()
        hr_contact_email = request.form.get("hr_contact_email", "").strip()
        hr_contact_phone = request.form.get("hr_contact_phone", "").strip()
        website = request.form.get("website", "").strip()
        industry = request.form.get("industry", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("register_company.html")

        user = User(email=email, role="company", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        company = Company(
            id=user.id,
            company_name=company_name,
            hr_contact_name=hr_contact_name,
            hr_contact_email=hr_contact_email,
            hr_contact_phone=hr_contact_phone,
            website=website,
            industry=industry,
            approval_status="Pending",
        )
        db.session.add(company)
        db.session.commit()

        flash("Company registration submitted. Wait for admin approval.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_company.html")


def redirect_by_role(user):
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    if user.role == "student":
        return redirect(url_for("student.dashboard"))
    if user.role == "company":
        return redirect(url_for("company.dashboard"))
    return redirect(url_for("auth.login"))
