import os

from flask import Flask

from extensions import db, login_manager
from auth_routes import auth_bp
from admin_routes import admin_bp
from company_routes import company_bp
from student_routes import student_bp
from models import seed_default_admin


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Basic configuration
    app.config["SECRET_KEY"] = "change-this-secret-key"
    # SQLite database will be created under instance/placement.db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "resumes"
    )

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Create database and seed admin
    with app.app_context():
        db.create_all()
        seed_default_admin()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(company_bp, url_prefix="/company")
    app.register_blueprint(student_bp, url_prefix="/student")

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)


