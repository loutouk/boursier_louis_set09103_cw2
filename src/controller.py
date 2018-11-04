import os
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from werkzeug.utils import secure_filename
from apiclient.http import MediaFileUpload
from customErrors import DriveFolderNil, DriveFileAdd
import unicodedata
from database import Database

UPLOAD_FOLDER = 'uploads'
DRIVE_FOLDER = "SetCloudDatas"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# If modifying these scopes, delete the file token.json.
API_SCOPES = 'https://www.googleapis.com/auth/drive'
# Every files should at least belong to the default set
DEFAULT_SET = "DefaultSet"

# Drive API
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', API_SCOPES)
	creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

class Controller:
	def __init__(self, app):
		self.app = app
		Session(self.app)
		self.bcrypt = Bcrypt(self.app)

	def indexPage(self):
		if session.get("user"):
			return self.homePage()
		return render_template('index.html', )

	def registerPage(self):
		return render_template('register.html', )

	def homePage(self):
		# List all files
		fileList = []
		results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name, webViewLink)").execute()
		items = results.get('files', [])
		if not items:
			fileList.append('No files found.')
		else:
			for item in items:
				fileList.append([item['name'],item['id'],item['webViewLink']])
		return render_template('home.html', content=fileList)

	def init_drive_folder(self):
		file_metadata = {
		    'name': DRIVE_FOLDER,
		    'mimeType': 'application/vnd.google-apps.folder'
		}
		file = drive_service.files().create(body=file_metadata, fields='id').execute()

	def get_drive_folder_id(self, folder_name):
		fileList = []
		results = drive_service.files().list(fields="files(id, name)").execute()
		items = results.get('files', [])
		if not items:
			raise DriveFolderNil("Error: no root file for the name " + folder_name)
		else:
			for item in items:
				if item['name'] == folder_name:
					return item['id']
			raise DriveFolderNil("Error: no root file for the name " + folder_name)

	def upload_file(self):

		if request.method == 'POST':

			db = Database("var/sqlite3.db")

			# check if the post request has the file part
			if 'fileToUpload' not in request.files:
				flash('No file part')
				return redirect(request.url)

			file = request.files['fileToUpload']
			# if user does not select file, browser also
			# submit an empty part without filename
			if file.filename == '':
				flash('No selected file')
				return redirect(request.url)

			root_folder = self.get_drive_folder_id(DRIVE_FOLDER)
			tags = []
			# every files should have the default set to perform operation on them
			tags.append(DEFAULT_SET)

			retrievedTags = request.form.get('tags')
			if(retrievedTags is not None):
				tagsList = retrievedTags.split(",")
				if(len(tagsList)>0):
					for tag in tagsList:
						tags.append(tag.encode('ascii','ignore').strip())

			if file and self.allowed_file(file.filename):
				filename = secure_filename(file.filename)

				# if filename already exists for this user in the datatabase, we cancel and inform the user
				fileExists = db.file_exists(filename, session["user"])
				if len(fileExists) > 0:
					flash('Error. File with this name already exists.')
					return redirect(url_for("homePage")) 

				file.save(os.path.join(UPLOAD_FOLDER, filename))
				file_metadata = {'name': filename, 'parents': [root_folder]}
				media = MediaFileUpload(os.path.join(UPLOAD_FOLDER, filename))
				file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
				# TODO remove the file from uploads, now that it is on drive
				if(file is None):
					raise DriveFileAdd("Error: could not add the file " + filename + " to the drive")
					flash('Error. File not uploaded.')
				else:
					# file was added to the drive folder, so we should update the database
					# create the file
					db.create_file(filename, session["user"])
					# if the set already exists, the query will be ignored
					for tag in tags:
						db.create_set(tag, session["user"])
					# link the file to the tags
					for tag in tags:
						db.associate_set_to_file(tag, filename, session["user"])
					flash('File uploaded.')
		


		return redirect(url_for("homePage")) 

	def allowed_file(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

	def login(self):
		if request.method == 'POST':
			db = Database("var/sqlite3.db", True)
			# no htmlentities() or equivalent because flask uses its own xss protection while using render_template()
			email = request.form.get('inputEmail')
			inputPassword = request.form.get('inputPassword')
			res = db.get_user_password(email)
			if not res or not self.bcrypt.check_password_hash(res[0][0], inputPassword):
				flash('Wrong credentials.')
			else:
				session["user"] = email
		return self.indexPage()

	def create_login(self):
		if request.method == 'POST':
			db = Database("var/sqlite3.db", True)
			# no htmlentities() or equivalent because flask uses its own xss protection while using render_template()
			email = request.form.get('inputEmail')
			password = request.form.get('inputPassword')	

			emailAlreadyTaken = db.user_exists(email)
			if emailAlreadyTaken:
				flash('Email already taken.')
				return self.indexPage()

			hashedPassword = self.bcrypt.generate_password_hash(password)
			res = db.create_user(email, hashedPassword, DEFAULT_SET)
			if res:
				flash('Account created. You can login.')
			else:
				flash('Failed to create account.')
		return self.indexPage()

	def logout(self):
		session.clear()
		return self.indexPage()