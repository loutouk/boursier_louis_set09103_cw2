import os
from flask import Flask, render_template, request, redirect, flash, url_for
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from werkzeug.utils import secure_filename
from apiclient.http import MediaFileUpload

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# If modifying these scopes, delete the file token.json.
API_SCOPES = 'https://www.googleapis.com/auth/drive'

# Drive API
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', API_SCOPES)
	creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

class Controller:
	def __init__(self, db):
		# Database
		self.db = db


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
		return render_template('index.html', content=fileList)

	def upload_file(self):
		file = request.form.get("fileToUpload", "")
		print file
		return render_template('index.html', content=[])

	def upload_file(self):
		if request.method == 'POST':
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
			if file and self.allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(UPLOAD_FOLDER, filename))
				file_metadata = {'name': filename}
				media = MediaFileUpload(os.path.join(UPLOAD_FOLDER, filename))
				file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
				# TODO remove the file from uploads, now that it is on drive
				flash('File uploaded')
		return redirect(url_for("index")) 

	def allowed_file(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS