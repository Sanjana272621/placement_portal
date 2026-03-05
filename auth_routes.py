from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, Student, Company

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        if current_user.role == "company":
            return redirect(url_for("company.dashboard"))
        if current_user.role == "student":
            return redirect(url_for("student.dashboard"))
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("auth.index"))
        flash("Invalid credentials or inactive account.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        roll_no = request.form.get("roll_no")
        phone = request.form.get("phone")
        department = request.form.get("department")
        cgpa = request.form.get("cgpa")
        batch_year = request.form.get("batch_year")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.register_student"))

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
        )
        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_student.html")


@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        hr_contact_name = request.form.get("hr_contact_name")
        hr_contact_email = request.form.get("hr_contact_email")
        website = request.form.get("website")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.register_company"))

        user = User(email=email, role="company", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        company = Company(
            id=user.id,
            company_name=company_name,
            hr_contact_name=hr_contact_name,
            hr_contact_email=hr_contact_email,
            website=website,
            approval_status="Pending",
        )
        db.session.add(company)
        db.session.commit()

        flash("Company registered successfully. Await admin approval.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_company.html")

