from flask import Flask
from config import Config
from app.extensions import db, login_manager, socketio


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.tickets import tickets_bp
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(dashboard_bp)

    from app import sockets  # noqa: F401 registers socket event handlers

    with app.app_context():
        db.create_all()

    return app
