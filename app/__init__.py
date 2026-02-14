from flask import Flask, g
from app.config import Config
from app.database import init_db, get_session


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_db(app)

    @app.before_request
    def before_request():
        g.db = get_session()

    @app.teardown_request
    def teardown_request(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
