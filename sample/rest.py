import threading
from flask import Flask

from deviceManager import device_api


class RestServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.app = Flask(__name__)
        self.app.register_blueprint(device_api)

    def run(self):
        self.app.run(host='0.0.0.0')
