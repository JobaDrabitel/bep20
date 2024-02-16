from flask import Flask
from app.ether.etherium import ether
from app.config import networks
from app.tron.trc20 import tron
def create_app():
    app = Flask(__name__)
    app.config['networks'] = networks
    app.register_blueprint(ether, url_prefix='')
    app.register_blueprint(tron, url_prefix='/trc20')

    return app
