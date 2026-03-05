from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from extensions import db
from models import User, Student, Company, PlacementDrive, Application

admin_bp = Blueprint("admin", __name__, template_folder="templates")


def admin_required():
    return current_user.is_authenticated and current_user.role == "admin"


@admin_bp.before_request
def restrict_to_admin():
    if not admin_required():
        return redirect(url_for("auth.login"))


@admin_bp.route("/dashboard")
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


@admin_bp.route("/companies")
def companies():
    search = request.args.get("search", "").strip()
    query = Company.query
    if search:
        query = query.filter(Company.company_name.ilike(f"%{search}%"))
    companies = query.all()
    return render_template("admin/companies.html", companies=companies, search=search)


@admin_bp.route("/companies/<int:company_id>/status", methods=["POST"])
def update_company_status(company_id):
    status = request.form.get("status")
    company = Company.query.get_or_404(company_id)
    company.approval_status = status
    db.session.commit()
    flash("Company status updated.", "success")
    return redirect(url_for("admin.companies"))


@admin_bp.route("/students")
def students():
    search = request.args.get("search", "").strip()
    query = Student.query.join(User)
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Student.name.ilike(like),
                Student.roll_no.ilike(like),
                Student.phone.ilike(like),
            )
        )
    students = query.all()
    return render_template("admin/students.html", students=students, search=search)


@admin_bp.route("/users/<int:user_id>/toggle_active", methods=["POST"])
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash("User active status updated.", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/drives")
def drives():
    drives = PlacementDrive.query.order_by(PlacementDrive.deadline.desc()).all()
    return render_template("admin/drives.html", drives=drives)


@admin_bp.route("/drives/<int:drive_id>/status", methods=["POST"])
def update_drive_status(drive_id):
    status = request.form.get("status")
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = status
    db.session.commit()
    flash("Drive status updated.", "success")
    return redirect(url_for("admin.drives"))


@admin_bp.route("/applications")
def applications():
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template("admin/applications.html", applications=applications)

