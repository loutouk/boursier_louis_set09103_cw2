import os
from flask import Flask, render_template, request, redirect, flash, url_for
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from werkzeug.utils import secure_filename
from apiclient.http import MediaFileUpload
from customErrors import DriveFolderNil, DriveFileAdd
import unicodedata

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

			root_folder = self.get_drive_folder_id(DRIVE_FOLDER)

			tags = []
			tags.append(DEFAULT_SET)

			retrievedTags = request.form.get('tags')
			if(retrievedTags is not None):
				tagsList = retrievedTags.split(",")
				if(len(tagsList)>0):
					for tag in tagsList:
						tags.append(tag.encode('ascii','ignore').strip())

			print tags

			# check if the post request has the file part
			if 'fileToUpload' not in request.files:
				flash('No file part')
				return redirect(request.url)
			file = request.files['fileToUpload']
			print file
			# if user does not select file, browser also
			# submit an empty part without filename
			if file.filename == '':
				flash('No selected file')
				return redirect(request.url)
			if file and self.allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(UPLOAD_FOLDER, filename))
				file_metadata = {'name': filename, 'parents': [root_folder]}
				media = MediaFileUpload(os.path.join(UPLOAD_FOLDER, filename))
				file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
				# TODO remove the file from uploads, now that it is on drive
				if(file is None):
					raise DriveFileAdd("Error: could not add the file " + filename + " to the drive")
					flash('Error. File not uploaded.')
				else:
					flash('File uploaded.')
		return redirect(url_for("index")) 

	def allowed_file(self, filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS