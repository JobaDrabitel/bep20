from flask import Flask
from app.ether.etherium import ether
from app.ether.config import  networks
def create_app():
    app = Flask(__name__)
    app.config['networks'] = networks
    app.register_blueprint(ether, url_prefix='')

    return app
