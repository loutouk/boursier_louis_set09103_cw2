# Author: Louis Boursier
# This class handles the data and database part of the application

import sqlite3

class Database:
	# by default, the database is regenerated
	def __init__(self, dbFileLocation, init = True):
		self.dbFileLocation = dbFileLocation
		self.conn = sqlite3.connect(self.dbFileLocation)
		if init:
			self.create_database()
			self.fill_database()

	# when the database object is destroyed, we also want to close the connection with the datatabse
	def __del__(self):
		self.conn.close()

	def fill_database(self):
		values = ["dummy"]
		self.conn.cursor().execute('INSERT INTO mydemo (name) VALUES(?)', values)
		self.conn.commit()

	def get_all(self):
		self.conn = sqlite3.connect(self.dbFileLocation)
		result = self.conn.cursor().execute('SELECT * FROM mydemo').fetchall()
		return result

	def create_database(self):
		query = """CREATE TABLE IF NOT EXISTS user(
					  id INTEGER PRIMARY KEY,
					  email TEXT NOT NULL,
					  password TEXT NOT NULL
					)"""
		self.conn.cursor().execute(query)
		self.conn.commit()

		query = """CREATE TABLE IF NOT EXISTS cloudset(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
		  FOREIGN KEY(userId) REFERENCES user(id) 
			  ON UPDATE CASCADE 
			  ON DELETE CASCADE 
		)"""
		self.conn.cursor().execute(query)
		self.conn.commit()

		query = """CREATE TABLE IF NOT EXISTS file(
		  id INTEGER PRIMARY KEY,
		  userId INTEGER,
		  name TEXT NOT NULL,
		  FOREIGN KEY(userId) REFERENCES user(id) 
		  	ON UPDATE CASCADE 
		  	ON DELETE CASCADE 
		)"""
		self.conn.cursor().execute(query)
		self.conn.commit()
		
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
		self.conn.cursor().execute(query)
		self.conn.commit()
