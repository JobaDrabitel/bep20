from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.bep20.routes import bep20

    app.register_blueprint(bep20, url_prefix='/bep20')

    return app
