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

	# we can destroy the table if it exists as this function is only called when we want to init the database
	def create_database(self):
		self.conn.cursor().execute('DROP TABLE IF EXISTS mydemo')
		self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS mydemo (name text)')
		self.conn.commit()

	def fill_database(self):
		values = ["dummy"]
		self.conn.cursor().execute('INSERT INTO mydemo (name) VALUES(?)', values)
		self.conn.commit()

	def get_all(self):
		self.conn = sqlite3.connect(self.dbFileLocation)
		result = self.conn.cursor().execute('SELECT * FROM mydemo').fetchall()
		return result