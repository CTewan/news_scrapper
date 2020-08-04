import os

from pymongo import MongoClient

from config import MONGODB_CONNECTION_STRING

mongodb_password = os.environ["mongodb_password"]

class DataBase(object):
	def __init__(self):
		self.client = None
		self.db = None
		self.available_sites = ["straits_times"]

	def connection(self):
		client = MongoClient(MONGODB_CONNECTION_STRING.format(mongodb_password))
		self.client = client

	def get_db(self):
		db = self.client.news_article
		self.db = db

	def get_collection(self, site):
		if site in self.available_sites:
			return self.db[site]

		return "Site not available. Please try again."

	def insert_data(self, collection, data):
		if type(data) == dict:
			collection.update_one({"_id": data["_id"]}, {"$set": data}, upsert=True)

		elif type(data) == list:
			for update_dict in data:
				collection.update_one({"_id": update_dict["_id"]}, {"$set": update_dict}, upsert=True)

if __name__ == "__main__":
	news_db = DataBase()
	news_db.connection()
	news_db.get_db()
	collection = news_db.get_collection(site="straits_times")


