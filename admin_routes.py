from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from extensions import db
from models import User, Student, Company, PlacementDrive, Application

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_only():
    return current_user.is_authenticated and current_user.role == "admin"


@admin_bp.before_request
def restrict_admin_routes():
    if not admin_only():
        return "Access denied", 403


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
    )


@admin_bp.route("/students")
@login_required
def students():
    q = request.args.get("q", "").strip()

    query = Student.query
    if q:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{q}%"),
                Student.roll_no.ilike(f"%{q}%"),
                Student.phone.ilike(f"%{q}%"),
            )
        )

    students = query.all()
    return render_template("admin/students.html", students=students, q=q)


@admin_bp.route("/companies")
@login_required
def companies():
    q = request.args.get("q", "").strip()

    query = Company.query
    if q:
        query = query.filter(
            or_(
                Company.company_name.ilike(f"%{q}%"),
                Company.industry.ilike(f"%{q}%"),
            )
        )

    companies = query.all()
    return render_template("admin/companies.html", companies=companies, q=q)


@admin_bp.route("/drives")
@login_required
def drives():
    drives = PlacementDrive.query.order_by(PlacementDrive.id.desc()).all()
    return render_template("admin/drives.html", drives=drives)


@admin_bp.route("/applications")
@login_required
def applications():
    applications = Application.query.order_by(Application.id.desc()).all()
    return render_template("admin/applications.html", applications=applications)


@admin_bp.route("/company/<int:company_id>/approve", methods=["POST"])
@login_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Approved"
    db.session.commit()
    flash(f"{company.company_name} approved successfully.", "success")
    return redirect(url_for("admin.companies"))


@admin_bp.route("/company/<int:company_id>/reject", methods=["POST"])
@login_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Rejected"
    db.session.commit()
    flash(f"{company.company_name} rejected.", "warning")
    return redirect(url_for("admin.companies"))


@admin_bp.route("/drive/<int:drive_id>/approve", methods=["POST"])
@login_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Approved"
    db.session.commit()
    flash(f"{drive.job_title} approved successfully.", "success")
    return redirect(url_for("admin.drives"))


@admin_bp.route("/drive/<int:drive_id>/reject", methods=["POST"])
@login_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Rejected"
    db.session.commit()
    flash(f"{drive.job_title} rejected.", "warning")
    return redirect(url_for("admin.drives"))


@admin_bp.route("/student/<int:student_id>/deactivate", methods=["POST"])
@login_required
def deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.user.is_active = False
    db.session.commit()
    flash(f"{student.name} has been deactivated.", "warning")
    return redirect(url_for("admin.students"))


@admin_bp.route("/company/<int:company_id>/deactivate", methods=["POST"])
@login_required
def deactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.user.is_active = False
    db.session.commit()
    flash(f"{company.company_name} has been deactivated.", "warning")
    return redirect(url_for("admin.companies"))