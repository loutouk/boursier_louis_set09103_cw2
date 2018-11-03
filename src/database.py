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

	def create_user(self, email, password):
		res = self.conn.cursor().execute('INSERT INTO user (email, password) VALUES(?, ?)', (email, password,))
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

	def create_database(self):
		query = """CREATE TABLE IF NOT EXISTS user(
					  id INTEGER PRIMARY KEY,
					  email TEXT NOT NULL UNIQUE,
					  password TEXT NOT NULL
					)"""
		res = self.conn.cursor().execute(query)

		query = """CREATE TABLE IF NOT EXISTS cloudset(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
		  FOREIGN KEY(userId) REFERENCES user(id) 
			  ON UPDATE CASCADE 
			  ON DELETE CASCADE 
		)"""
		res = self.conn.cursor().execute(query)

		query = """CREATE TABLE IF NOT EXISTS file(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
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