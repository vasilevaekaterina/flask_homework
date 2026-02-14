from flask import Flask, g, request
from app.config import Config
from app.database import init_db, get_session


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_db(app)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.before_request
    def before_request():
        if request.method == "OPTIONS":
            return "", 204
        if request.path.startswith("/api"):
            g.db = get_session()

    @app.teardown_request
    def teardown_request(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return (
            "API объявлений. Эндпоинты: "
            "GET/POST /api/advertisements, "
            "GET/PUT/DELETE /api/advertisements/<id>"
        ), 200

    return app
