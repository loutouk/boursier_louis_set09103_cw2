from flask import Flask, render_template
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'
# Drive API
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

class Controller:
	def __init__(self, db):
		# Database
		self.db = db


	def homePage(self):
		# List all files
		fileList = []
		results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, webViewLink)").execute()
		items = results.get('files', [])
		if not items:
			fileList.append('No files found.')
		else:
			for item in items:
				fileList.append([item['name'],item['id'],item['webViewLink']])
		return render_template('index.html', content=fileList)