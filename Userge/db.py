from pymongo import MongoClient
from .utils import Config, logging


class Database:

    def __init__(self, tablename):
        client = MongoClient(Config.DB_URI)
        self.db = client[tablename]

    def addnew(self, dictionary):
        result = self.db.reviews.insert_one(dictionary)
        return result

    def findone(self, key, value: object) -> object:
        return self.db.reviews.find_one({key: value})

    def update(self, existingentry, new_dictionary_entry, set_unset):
        if set_unset is 'set':
            x = '$set'
        else:
            x = '$unset'
        result = self.db.reviews.update_one(existingentry, {x: new_dictionary_entry})
        return result

    def delall(self):
        self.db.reviews.drop()

    def filter(self, query: dict, output: dict):
        return self.db.reviews.find(query, output)

    def never_used(self, output: dict):
        return self.filter({"times_used": {'exists': False}}, output)
