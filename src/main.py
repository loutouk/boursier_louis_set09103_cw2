#Author: Louis Boursier

# Main script, handles the routes and the reception/endpoint of the html form
# The host and port can easily by change thanks to the global variables below

from flask import Flask
from controller import Controller
import os

AUTHOR="Louis Boursier"
TITLE="SetCloud"
HOST="0.0.0.0"
PORT=9114
DEBUG=True

def main(app, controller):
	app.add_url_rule('/testPage', 'testPage', lambda: controller.testPage())

	app.add_url_rule('/', 'indexPage', lambda: controller.indexPage())
	app.add_url_rule('/register', 'registerPage', lambda: controller.registerPage())
	app.add_url_rule('/home', 'homePage', lambda: controller.homePage())
	app.add_url_rule('/login', 'login', lambda: controller.login(), methods=['POST'])
	app.add_url_rule('/create_login', 'create_login', lambda: controller.create_login(), methods=['POST'])
	app.add_url_rule('/upload_file', 'upload_file', lambda: controller.upload_file(), methods=['POST'])
	app.add_url_rule('/logout', 'logout', lambda: controller.logout(), methods=['POST'])
	app.register_error_handler(404, lambda x: controller.page_not_found())
	app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)

if __name__ == "__main__":
	app = Flask(__name__)
	app.secret_key = os.urandom(24)
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	controller = Controller(app)
	main(app, controller)
