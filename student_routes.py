import os
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from extensions import db
from models import Student, PlacementDrive, Application, Company

student_bp = Blueprint("student", __name__, url_prefix="/student")


def student_only():
    return current_user.is_authenticated and current_user.role == "student"


@student_bp.before_request
def restrict_student_routes():
    if not student_only():
        return "Access denied", 403


@student_bp.route("/dashboard")
@login_required
def dashboard():
    approved_drives = (
        PlacementDrive.query.filter_by(status="Approved")
        .order_by(PlacementDrive.id.desc())
        .all()
    )

    my_applications = (
        Application.query.filter_by(student_id=current_user.id)
        .order_by(Application.id.desc())
        .all()
    )

    return render_template(
        "student/dashboard.html",
        approved_drives=approved_drives,
        my_applications=my_applications,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    student = Student.query.get_or_404(current_user.id)

    if request.method == "POST":
        student.name = request.form.get("name", "").strip()
        student.phone = request.form.get("phone", "").strip()
        student.department = request.form.get("department", "").strip()
        student.cgpa = float(request.form.get("cgpa"))
        student.batch_year = int(request.form.get("batch_year"))

        resume = request.files.get("resume")
        if resume and resume.filename:
            filename = secure_filename(resume.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "resumes")
            os.makedirs(upload_folder, exist_ok=True)
            resume.save(os.path.join(upload_folder, filename))
            student.resume_filename = filename

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)


@student_bp.route("/jobs")
@login_required
def jobs():
    q = request.args.get("q", "").strip()

    query = PlacementDrive.query.join(Company).filter(PlacementDrive.status == "Approved")

    if q:
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(f"%{q}%"),
                PlacementDrive.required_skills.ilike(f"%{q}%"),
                Company.company_name.ilike(f"%{q}%"),
            )
        )

    drives = query.order_by(PlacementDrive.id.desc()).all()
    return render_template("student/jobs.html", drives=drives, q=q)


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@login_required
def apply(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "Approved":
        flash("You can only apply to approved placement drives.", "danger")
        return redirect(url_for("student.jobs"))

    existing = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive.id
    ).first()

    if existing:
        flash("You have already applied to this placement drive.", "warning")
        return redirect(url_for("student.jobs"))

    application = Application(
        student_id=current_user.id,
        drive_id=drive.id,
        status="Applied",
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully.", "success")
    return redirect(url_for("student.my_applications"))


@student_bp.route("/applications")
@login_required
def my_applications():
    applications = (
        Application.query.filter_by(student_id=current_user.id)
        .order_by(Application.id.desc())
        .all()
    )
    return render_template("student/my_applications.html", applications=applications)