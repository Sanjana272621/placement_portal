import os
from flask import Flask
from extensions import db, login_manager
from models import seed_default_admin

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"

    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "placement.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        seed_default_admin()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)