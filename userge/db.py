from pymongo import MongoClient
from pymongo.cursor import Cursor
from typing import Dict, Union
from .utils import Config, logging

MGCLIENT = MongoClient(Config.DB_URI)

MONGODICT = Dict[str, Union[int, str, bool]]


class Database:
    def __init__(
        self,
        tablename: str
    ) -> None:

        self.log = logging.getLogger(__name__)
        self.name = tablename
        self.db = MGCLIENT[tablename]

        self.log.info(
            f"Creating Table => {tablename}"
        )

    @classmethod
    def create_table(
        cls,
        tablename: str
    ) -> 'Database':

        return cls(tablename)

    def insert_one(
        self,
        dict_: MONGODICT
    ) -> Cursor:

        self.log.info(
            f"{self.name} :: Inserting {dict_}"
        )

        return self.db.reviews.insert_one(dict_)

    def update_one(
        self,
        existingentry: MONGODICT,
        new_dictionary_entry: MONGODICT,
    ) -> Cursor:

        self.log.info(
            f"{self.name} :: Updating {existingentry} To {new_dictionary_entry}"
        )

        return self.db.reviews.update_one(
            existingentry,
            {'$set': new_dictionary_entry}
        )

    def delete_one(
        self,
        dict_: MONGODICT
    ) -> Cursor:

        self.log.info(
            f"{self.name} :: Deleting {dict_}"
        )

        return self.db.reviews.delete_one(dict_)

    def find_one(
        self,
        key: str,
        value: Union[int, str, bool]
    ) -> Cursor:

        dict_ = {key: value}

        self.log.info(
            f"{self.name} :: Finding One {dict_}"
        )

        ret_val = dict(self.db.reviews.find_one(dict_) or {})

        self.log.info(
            f"{self.name} :: Found {ret_val} For {dict_}"
        )

        return ret_val

    def find_all(
        self,
        query: MONGODICT,
        output: MONGODICT
    ) -> Cursor:

        self.log.info(
            f"{self.name} :: Finding All For {query}, Requesting {output}"
        )

        ret_val = list(self.db.reviews.find(query, output) or [])

        self.log.info(
            f"{self.name} :: Found {ret_val} For {query}, Requesting {output}"
        )

        return ret_val

    def delete_table(self) -> None:

        self.log.info(
            f"WARNING! :: Droping {self.name}"
        )

        self.db.reviews.drop()