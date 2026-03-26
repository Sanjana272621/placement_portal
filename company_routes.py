from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import (
    Company,
    PlacementDrive,
    Application,
    Student,
    ApplicationStatusHistory,
    Notification,
)

company_bp = Blueprint("company", __name__, url_prefix="/company")


def company_only():
    return current_user.is_authenticated and current_user.role == "company"


@company_bp.before_request
def restrict_company_routes():
    if not company_only():
        return "Access denied", 403

    company = Company.query.get(current_user.id)
    if not company or company.approval_status != "Approved":
        return "Company not approved", 403


@company_bp.route("/dashboard")
@login_required
def dashboard():
    company = Company.query.get_or_404(current_user.id)
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.id.desc()).all()

    applicant_counts = {}
    for drive in drives:
        applicant_counts[drive.id] = Application.query.filter_by(drive_id=drive.id).count()

    return render_template(
        "company/dashboard.html",
        company=company,
        drives=drives,
        applicant_counts=applicant_counts,
    )


@company_bp.route("/drives/create", methods=["GET", "POST"])
@login_required
def create_drive():
    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        job_description = request.form.get("job_description", "").strip()
        eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
        min_cgpa = request.form.get("min_cgpa", "").strip()
        deadline = request.form.get("deadline", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        experience_required = request.form.get("experience_required", "").strip()
        salary_range = request.form.get("salary_range", "").strip()

        drive = PlacementDrive(
            company_id=current_user.id,
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility_criteria,
            min_cgpa=float(min_cgpa),
            deadline=deadline,
            required_skills=required_skills,
            experience_required=experience_required,
            salary_range=salary_range,
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()

        flash("Job position created and sent for admin approval.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/create_drive.html")


@company_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@login_required
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != current_user.id:
        return "Access denied", 403

    if request.method == "POST":
        drive.job_title = request.form.get("job_title", "").strip()
        drive.job_description = request.form.get("job_description", "").strip()
        drive.eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
        drive.min_cgpa = float(request.form.get("min_cgpa", "").strip())
        drive.deadline = request.form.get("deadline", "").strip()
        drive.required_skills = request.form.get("required_skills", "").strip()
        drive.experience_required = request.form.get("experience_required", "").strip()
        drive.salary_range = request.form.get("salary_range", "").strip()

        db.session.commit()
        flash("Job position updated successfully.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/edit_drive.html", drive=drive)


@company_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@login_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != current_user.id:
        return "Access denied", 403

    drive.status = "Closed"
    db.session.commit()
    flash("Job position closed.", "warning")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drives/<int:drive_id>/applications")
@login_required
def drive_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != current_user.id:
        return "Access denied", 403

    applications = Application.query.filter_by(drive_id=drive.id).order_by(Application.id.desc()).all()
    return render_template("company/applications.html", drive=drive, applications=applications)


@company_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@login_required
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)

    if application.drive.company_id != current_user.id:
        return "Access denied", 403

    new_status = request.form.get("status", "").strip()

    allowed_statuses = ["Shortlisted", "Selected", "Rejected"]
    if new_status not in allowed_statuses:
        flash("Invalid status.", "danger")
        return redirect(url_for("company.drive_applications", drive_id=application.drive_id))

    from_status = application.status

    # Backfill: if this application has no history yet (apps created before this milestone),
    # store the current status as the first timeline entry.
    if not ApplicationStatusHistory.query.filter_by(application_id=application.id).first():
        db.session.add(
            ApplicationStatusHistory(
                application_id=application.id,
                from_status=None,
                to_status=from_status,
                changed_by_user_id=None,
                changed_by_role="system",
            )
        )

    application.status = new_status

    # Persist the transition for a complete application history.
    db.session.add(
        ApplicationStatusHistory(
            application_id=application.id,
            from_status=from_status,
            to_status=new_status,
            changed_by_user_id=current_user.id,
            changed_by_role=current_user.role,
        )
    )

    # Notify the student about the status update.
    drive = application.drive
    company_name = drive.company.company_name
    job_title = drive.job_title
    if new_status == "Shortlisted":
        message = f"Your application for '{job_title}' at {company_name} has been shortlisted."
    elif new_status == "Selected":
        message = f"Your application for '{job_title}' at {company_name} has been selected."
    else:  # Rejected
        message = f"Your application for '{job_title}' at {company_name} has been rejected."

    db.session.add(
        Notification(
            user_id=application.student_id,
            message=message,
        )
    )
    db.session.commit()
    flash("Application status updated.", "success")
    return redirect(url_for("company.drive_applications", drive_id=application.drive_id))


@company_bp.route("/students/<int:student_id>")
@login_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("company/applicant_profile.html", student=student)


@company_bp.route("/applications/<int:application_id>/history")
@login_required
def application_history(application_id: int):
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != current_user.id:
        return "Access denied", 403

    history = (
        ApplicationStatusHistory.query.filter_by(application_id=application.id)
        .order_by(ApplicationStatusHistory.changed_at.asc())
        .all()
    )
    placement = getattr(application, "placement", None)

    return render_template(
        "company/application_history.html",
        application=application,
        history=history,
        placement=placement,
    )