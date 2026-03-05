from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_required, current_user

from extensions import db
from models import Company, PlacementDrive, Application

company_bp = Blueprint("company", __name__, template_folder="templates")


def company_required():
    return current_user.is_authenticated and current_user.role == "company"


@company_bp.before_request
def restrict_to_company():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.get(current_user.id)
    if not company or company.approval_status != "Approved":
        flash("Company not approved yet.", "warning")
        return redirect(url_for("auth.index"))


@company_bp.route("/dashboard")
@login_required
def dashboard():
    company = Company.query.get_or_404(current_user.id)
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_applicants = {
        drive.id: Application.query.filter_by(drive_id=drive.id).count()
        for drive in drives
    }
    return render_template(
        "company/dashboard.html",
        company=company,
        drives=drives,
        drive_applicants=drive_applicants,
    )


@company_bp.route("/drives/new", methods=["GET", "POST"])
@login_required
def create_drive():
    if request.method == "POST":
        job_title = request.form.get("job_title")
        job_description = request.form.get("job_description")
        eligibility_criteria = request.form.get("eligibility_criteria")
        min_cgpa = float(request.form.get("min_cgpa"))
        deadline = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d").date()

        drive = PlacementDrive(
            company_id=current_user.id,
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility_criteria,
            min_cgpa=min_cgpa,
            deadline=deadline,
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()
        flash("Placement drive created. Await admin approval.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/create_drive.html")


@company_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@login_required
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        return redirect(url_for("company.dashboard"))

    if request.method == "POST":
        drive.job_title = request.form.get("job_title")
        drive.job_description = request.form.get("job_description")
        drive.eligibility_criteria = request.form.get("eligibility_criteria")
        drive.min_cgpa = float(request.form.get("min_cgpa"))
        drive.deadline = datetime.strptime(
            request.form.get("deadline"), "%Y-%m-%d"
        ).date()
        db.session.commit()
        flash("Drive updated.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/edit_drive.html", drive=drive)


@company_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@login_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        return redirect(url_for("company.dashboard"))
    drive.status = "Closed"
    db.session.commit()
    flash("Drive closed.", "info")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drives/<int:drive_id>/applications")
@login_required
def view_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        return redirect(url_for("company.dashboard"))
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template(
        "company/applications.html", drive=drive, applications=applications
    )


@company_bp.route(
    "/applications/<int:application_id>/status", methods=["POST"]
)
@login_required
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    drive = application.drive
    if drive.company_id != current_user.id:
        return redirect(url_for("company.dashboard"))
    status = request.form.get("status")
    application.status = status
    db.session.commit()
    flash("Application status updated.", "success")
    return redirect(url_for("company.view_applications", drive_id=drive.id))

