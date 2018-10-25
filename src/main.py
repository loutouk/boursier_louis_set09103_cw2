#Author: Louis Boursier

# Main script, handles the routes and the reception/endpoint of the html form
# The host and port can easily by change thanks to the global variables below

from flask import Flask, redirect, url_for, render_template, request, jsonify, abort
from controller import Controller
from database import Database

AUTHOR="Louis Boursier"
TITLE="SetCloud"
HOST="0.0.0.0"
PORT=9114
DEBUG=True

def main(app, controller):
	app.add_url_rule('/', 'index', lambda: controller.homePage())
	app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)

if __name__ == "__main__":
	app = Flask(__name__)
	db = Database("var/sqlite3.db")
	controller = Controller(db)
	main(app, controller)
