#Author: Louis Boursier

# Main script, handles the routes and the reception/endpoint of the html form
# The host and port can easily by change thanks to the global variables below

from flask import Flask
from controller import Controller
from database import Database

AUTHOR="Louis Boursier"
TITLE="SetCloud"
HOST="0.0.0.0"
PORT=9114
DEBUG=True

def main(app, controller):
	app.add_url_rule('/', 'index', lambda: controller.homePage())
	app.add_url_rule('/upload_file', 'upload_file', lambda: controller.upload_file(), methods=['POST'])
	app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)

if __name__ == "__main__":
	app = Flask(__name__)
	app.secret_key = "e6fe.16U.fe8!?./AZ5^"
	db = Database("var/sqlite3.db")
	controller = Controller(db)
	main(app, controller)
