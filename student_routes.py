import os
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import Student, PlacementDrive, Application

student_bp = Blueprint("student", __name__, template_folder="templates")


def student_required():
    return current_user.is_authenticated and current_user.role == "student"


@student_bp.before_request
def restrict_to_student():
    # Allow resume uploads and dashboard only for logged-in students
    if not request.endpoint:
        return
    if not student_required() and not request.endpoint.endswith("static"):
        return redirect(url_for("auth.login"))


@student_bp.route("/dashboard")
@login_required
def dashboard():
    student = Student.query.get_or_404(current_user.id)

    # Approved drives only and where student meets CGPA and before deadline
    today = datetime.utcnow().date()
    approved_drives = (
        PlacementDrive.query.filter_by(status="Approved")
        .filter(PlacementDrive.deadline >= today)
        .filter(PlacementDrive.min_cgpa <= student.cgpa)
        .all()
    )

    applications = (
        Application.query.filter_by(student_id=student.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    applied_drive_ids = {app.drive_id for app in applications}

    return render_template(
        "student/dashboard.html",
        student=student,
        approved_drives=approved_drives,
        applications=applications,
        applied_drive_ids=applied_drive_ids,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    student = Student.query.get_or_404(current_user.id)

    if request.method == "POST":
        student.name = request.form.get("name")
        student.roll_no = request.form.get("roll_no")
        student.phone = request.form.get("phone")
        student.department = request.form.get("department")
        student.cgpa = float(request.form.get("cgpa"))
        student.batch_year = int(request.form.get("batch_year"))

        file = request.files.get("resume")
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            student.resume_filename = filename

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)


@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@login_required
def apply_drive(drive_id):
    student = Student.query.get_or_404(current_user.id)
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "Approved":
        flash("You can only apply to approved drives.", "warning")
        return redirect(url_for("student.dashboard"))

    existing = Application.query.filter_by(
        student_id=student.id, drive_id=drive.id
    ).first()
    if existing:
        flash("You have already applied to this drive.", "info")
        return redirect(url_for("student.dashboard"))

    application = Application(student_id=student.id, drive_id=drive.id)
    db.session.add(application)
    db.session.commit()
    flash("Application submitted.", "success")
    return redirect(url_for("student.dashboard"))


@student_bp.route("/applications")
@login_required
def applications():
    student = Student.query.get_or_404(current_user.id)
    applications = (
        Application.query.filter_by(student_id=student.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template(
        "student/applications.html",
        student=student,
        applications=applications,
    )

