# Author: Louis Boursier
# This class handles the data and database part of the application

import sqlite3

class Database:
	# by default, the database is regenerated
	def __init__(self, dbFileLocation, init = False):
		self.dbFileLocation = dbFileLocation
		self.conn = sqlite3.connect(self.dbFileLocation)
		if init:
			self.create_database()

	# when the database object is destroyed, we also want to close the connection with the datatabse
	def __del__(self):
		self.conn.close()

	def create_user(self, email, password, initialSet):
		# we create automatically and transparently the first set for the user
		# we want to have both operations successful, or we cancel everything, hence the transaction
		res = self.conn.cursor().execute('INSERT INTO user (email, password) VALUES(?, ?)', (email, password,))
		res = self.conn.cursor().execute('INSERT INTO cloudset (name, userId) VALUES(?, (SELECT id from user where email = ?))', (initialSet,email,))
		self.conn.commit()
		return res

	def get_user_password(self, email):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('SELECT password FROM user where email = ?', (email,)).fetchall()
		return res

	def user_exists(self, email):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('SELECT email FROM user where email = ?', (email,)).fetchall()
		return res

	def file_exists(self, fileName, userEmail):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('SELECT file.name FROM file INNER JOIN user ON user.id = file.userId where user.email = ? AND file.name = ?', (userEmail,fileName,)).fetchall()
		return res

	def set_exists(self, setName, userEmail):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('SELECT cloudset.name FROM cloudset INNER JOIN user ON user.id = cloudset.userId where user.email = ? AND cloudset.name = ?', (userEmail,setName,)).fetchall()
		return res

	def create_file(self, fileName, driveId, userEmail):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('INSERT INTO file (name, driveId, userId)  VALUES(?, ?, (select id from user where email = ?))', (fileName,driveId,userEmail,)).fetchall()
		self.conn.commit()
		return res

	def create_set(self, setName, userEmail):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('INSERT INTO cloudset (name, userId)  VALUES(?, (select id from user where email = ?))', (setName,userEmail,)).fetchall()
		self.conn.commit()
		return res

	def associate_set_to_file(self, setName, fileName, userEmail):
		self.conn = sqlite3.connect(self.dbFileLocation)
		res = self.conn.cursor().execute('''INSERT INTO cloudsetMapFile (fileId, cloudsetId)  
			VALUES((select file.id from file INNER JOIN user ON user.id = file.userId where user.email = :email and file.name = :fileName), 
			(select cloudset.id from cloudset INNER JOIN user ON user.id = cloudset.userId where user.email = :email and cloudset.name = :setName))''', 
			{"email":userEmail, "setName":setName, "fileName":fileName}).fetchall()
		self.conn.commit()
		return res

	def create_database(self):
		query = """CREATE TABLE IF NOT EXISTS user(
					  id INTEGER PRIMARY KEY,
					  email TEXT NOT NULL UNIQUE ON CONFLICT IGNORE,
					  password TEXT NOT NULL
					)"""
		res = self.conn.cursor().execute(query)

		query = """CREATE TABLE IF NOT EXISTS cloudset(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
		  UNIQUE(userId, name) ON CONFLICT IGNORE,
		  FOREIGN KEY(userId) REFERENCES user(id) 
			  ON UPDATE CASCADE 
			  ON DELETE CASCADE 
		)"""
		res = self.conn.cursor().execute(query)

		query = """CREATE TABLE IF NOT EXISTS file(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
		  driveId TEXT NOT NULL,
		  UNIQUE(userId, name) ON CONFLICT IGNORE,
		  FOREIGN KEY(userId) REFERENCES user(id) 
		  	ON UPDATE CASCADE 
		  	ON DELETE CASCADE 
		)"""
		res = self.conn.cursor().execute(query)
		
		query = """CREATE TABLE IF NOT EXISTS cloudsetMapFile(
		  id INTEGER PRIMARY KEY,
		  cloudsetId INTEGER,
		  fileId INTEGER,
		  FOREIGN KEY(cloudsetId) REFERENCES cloudset(id) 
			  ON UPDATE CASCADE 
			  ON DELETE CASCADE,
		  FOREIGN KEY(fileId) REFERENCES file(id) 
			  ON UPDATE CASCADE 
			  ON DELETE CASCADE 
		)"""
		res = self.conn.cursor().execute(query)
		self.conn.commit()