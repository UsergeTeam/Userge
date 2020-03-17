from pymongo import MongoClient
from typing import Dict, Any
from .utils import Config, logging

mgclient = MongoClient(Config.DB_URI)


class Database:
    def __init__(self, tablename: str) -> None:
        self.db = mgclient[tablename]

    @classmethod
    def create_table(cls, tablename: str) -> 'Database':
        return cls(tablename)

    def insert_one(self, dict_: Dict[str, Any]) -> object:
        return self.db.reviews.insert_one(dict_)

    def update_one(
        self,
        existingentry: Dict[str, Any],
        new_dictionary_entry: Dict[str, Any],
    ) -> object:

        return self.db.reviews.update_one(
            existingentry,
            {'$set': new_dictionary_entry}
        )

    def delete_one(self, dict_: Dict[str, Any]) -> object:
        return self.db.reviews.delete_one(dict_)

    def find_one(self, key: str, value: Any) -> object:
        return self.db.reviews.find_one({key: value})

    def find_all(
        self,
        query: Dict[str, Any],
        output: Dict[str, Any]
    ) -> object:

        return self.db.reviews.find(query, output)

    def delete_table(self) -> None:
        self.db.reviews.drop()