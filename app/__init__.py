from flask import Flask, request
import os

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

from config import Config
from app.translations import LANGUAGES, TRANSLATIONS


db = SQLAlchemy()

login_manager = LoginManager()



def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )


    # Load configuration
    app.config.from_object(Config)



    # Session config (filesystem backend to avoid cookie size limits)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = os.path.join(app.instance_path, "flask_session")
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_FILE_THRESHOLD"] = 100

    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

    Session(app)

    # Initialize extensions
    db.init_app(app)

    login_manager.init_app(app)


    # Language handling (cookie based, falls back to English)
    @app.before_request
    def load_language():

        lang = request.cookies.get("dc-lang", "en")

        from flask import g

        g.lang = lang if lang in LANGUAGES else "en"


    @app.context_processor
    def inject_translations():

        from flask import g

        current = g.get("lang", "en")

        table = TRANSLATIONS.get(current, {})

        def t(text):
            return table.get(text, text)

        return {
            "t": t,
            "lang": current,
            "languages": LANGUAGES,
        }


    # Login route
    login_manager.login_view = "auth.login"



    # User loader (for Flask-Login)
    from app.models.user import User
    from app.models import analysis as _analysis_models  # noqa: F401 - registers tables
    from app.models import alerts as _alert_models  # noqa: F401 - registers alert tables


    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )



    # Create database tables
    with app.app_context():

        db.create_all()



    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.assistant import assistant
    from app.routes.alerts import alerts
    from app.routes.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(assistant)
    app.register_blueprint(alerts)
    app.register_blueprint(admin)



    return app