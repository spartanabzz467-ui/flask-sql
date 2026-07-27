import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_overrides=None):
    """Application factory. Keeps app creation testable and modular."""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.compact = False

    if config_overrides:
        app.config.update(config_overrides)

    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.resources.workouts import workouts_bp
    from app.resources.exercises import exercises_bp

    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)

    @app.route("/")
    def index():
        return {"message": "Workout Tracker API is running"}, 200

    return app
