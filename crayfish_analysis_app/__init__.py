from flask import Flask
from .models import db, login_manager
from .dash_app.app import create_dash_app


def create_app(config_class_name):
    """Create and configure the Flask app"""
    app = Flask(__name__)

    app.config.from_object(config_class_name)

    from crayfish_analysis_app.views import main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    db.init_app(app)

    create_dash_app(app)

    with app.app_context():
        db.create_all()
        print("Database created successfully!")

    login_manager.init_app(app)

    return app
