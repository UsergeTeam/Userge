from pymongo import MongoClient
from pymongo.cursor import Cursor
from typing import Dict, Any
from .utils import Config, logging

log = logging.getLogger(__name__)

mgclient = MongoClient(Config.DB_URI)


class Database:
    def __init__(
        self,
        tablename: str
    ) -> None:

        self.name = tablename
        self.db = mgclient[tablename]

    @classmethod
    def create_table(
        cls,
        tablename: str
    ) -> 'Database':

        log.info(
            f"Creating Table => {tablename}"
        )

        return cls(tablename)

    def insert_one(
        self,
        dict_: Dict[str, Any]
    ) -> Cursor:

        log.info(
            f"{self.name} :: Inserting {dict_}"
        )

        return self.db.reviews.insert_one(dict_)

    def update_one(
        self,
        existingentry: Dict[str, Any],
        new_dictionary_entry: Dict[str, Any],
    ) -> Cursor:

        log.info(
            f"{self.name} :: Updating {existingentry} To {new_dictionary_entry}"
        )

        return self.db.reviews.update_one(
            existingentry,
            {'$set': new_dictionary_entry}
        )

    def delete_one(
        self,
        dict_: Dict[str, Any]
    ) -> Cursor:

        log.info(
            f"{self.name} :: Deleting {dict_}"
        )

        return self.db.reviews.delete_one(dict_)

    def find_one(
        self,
        key: str,
        value: Any
    ) -> Cursor:

        dict_ = {key: value}

        log.info(
            f"{self.name} :: Finding One {dict_}"
        )
    
        return self.db.reviews.find_one(dict_)

    def find_all(
        self,
        query: Dict[str, Any],
        output: Dict[str, Any]
    ) -> Cursor:

        log.info(
            f"{self.name} :: Finding All For {query}, Requesting {output}"
        )

        return self.db.reviews.find(query, output)

    def delete_table(self) -> None:

        log.info(
            f"WARNING! :: Droping {self.name}"
        )

        self.db.reviews.drop()