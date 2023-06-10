# General Imports
from __future__ import annotations # For self-referential type-hints
from pathlib import Path
import os
from abc import abstractmethod, ABC
from typing import Union, Any
import json
import sqlite3

# Package Imports
from .path_handling import CONFIG_PATH

class DatabaseHandler(ABC):

    def __init__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def find_one(cls, database : str, **fields) -> tuple(Any):
        pass

    @classmethod
    @abstractmethod
    def find_many(cls, database : str, **fields) -> list(tuple(Any)):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, database, **fields) -> bool:
        pass

    @classmethod
    @abstractmethod
    def update(cls, database : str, setfields, **condfields) -> bool:
        pass

    @classmethod
    @abstractmethod
    def insert(cls, database : str, **fields) -> int:
        pass

class SQLiteDatabaseHandler(DatabaseHandler):

    DB_CONNECTION : sqlite3.Connection = None

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")
    
    @classmethod
    def _get_db(cls) -> sqlite3.Connection:
        if not SQLiteDatabaseHandler.DB_CONNECTION:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                DB_PATH = Path(os.path.expanduser(cfg["DB_PATH"]))
                cls.DB_CONNECTION = sqlite3.connect(DB_PATH)
        return cls.DB_CONNECTION
    
    @classmethod
    def _sql_where_str_builder(cls, fields : dict[str, Any]) -> tuple(str, list(Any)):
        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        sql = ""
        if len(values) > 0:
            sql += f" WHERE {keys[0]} = ? "
            for i in range(1, len(values)):
                sql += f"AND {keys[i]} = ? "
        return sql, values
    
    @classmethod
    def _sql_set_str_builder(cls, fields : dict[str, Any]) -> tuple(str, list(Any)):
        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        sql = ""
        if len(values) > 0:
            sql += f" SET {keys[0]} = ?"
            for i in range(1, len(values)):
                sql += f", {keys[i]} = ?"
        return sql, values

    @classmethod
    def find_one(cls, database, **fields) -> tuple(Any):
        sql, values = cls._sql_where_str_builder(fields)
        sql = f"SELECT * from {database}" + sql
        result = cls._get_db().cursor().execute(sql, values).fetchone()
        return result

    @classmethod
    def find_many(cls, database, **fields) -> list(tuple(Any)):
        sql, values = cls._sql_where_str_builder(fields)
        sql = f"SELECT * from {database}" + sql
        results = cls._get_db().cursor().execute(sql, values).fetchall()
        return results

    @classmethod
    def delete(cls, database, **fields) -> bool:
        db = cls._get_db()
        cursor = db.cursor()
        sql, values = cls._sql_where_str_builder(fields)
        sql = f"DELETE FROM {database}" + sql
        cursor.execute(sql, values)
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def update(cls, database : str, setfields, **condfields) -> bool:
        db = cls._get_db()
        cursor = db.cursor()
        setsql, setvalues = cls._sql_set_str_builder(setfields)
        wheresql, wherevalues = cls._sql_where_str_builder(condfields)
        sql = f"UPDATE {database}" + setsql + wheresql
        values = setvalues + wherevalues
        cursor.execute(sql, values)
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def insert(cls, database : str, **fields) -> int:
        db = cls._get_db()
        cursor = db.cursor()
        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        # Insert string builder
        sql = f"INSERT INTO {database}("
        values_str = " VALUES("
        for key in keys:
            sql += f"{key},"
            values_str += "?,"
        values_str = values_str[:-1] + ")"
        sql = sql[:-1] + ")" + values_str
        # Insertion
        cursor.execute(sql, values)
        db.commit()
        return cursor.lastrowid

class DatabaseEntity(ABC):

    db_handler : DatabaseHandler = SQLiteDatabaseHandler
    
    def __init__(self, database : str, id : Union[int, None] = None) -> None:
        super().__init__()
        self.id = id    # None if not presently in the database, else the internal db id.
        self.database = database
    
    def save(self, **kwargs) -> int:
        if (self.id is None):
            self.id = self.db_handler.insert(self.database, **kwargs)
        else:
            self.db_handler.update(self.database, kwargs, id=self.id)
        return self.id
            
    @classmethod
    @abstractmethod
    def find(cls, **kwargs) -> list[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def get(cls, id : int) -> DatabaseEntity:
        pass

    @classmethod
    def delete(cls, database : str, id : int) -> bool:
        return cls.db_handler.delete(database, id=id)

    def __eq__(self, other : DatabaseEntity) -> bool:
        return self.id == other.id
    
class SQLiteTableInstantiator():
    
    DB_CONNECTION : sqlite3.Connection = None

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")
    
    @classmethod
    def _get_db(cls) -> sqlite3.Connection:
        if not SQLiteDatabaseHandler.DB_CONNECTION:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                DB_PATH = Path(os.path.expanduser(cfg["DB_PATH"]))
                cls.DB_CONNECTION = sqlite3.connect(DB_PATH)
        return cls.DB_CONNECTION

    @classmethod
    def run(cls):
        cls.staff_table()
        cls.consumable_table()

    @classmethod
    def consumable_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS consumables(
            id INTEGER PRIMARY KEY NOT NULL UNIQUE DEFAULT 0,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            major_parts INTEGER NOT NULL DEFAULT 0,
            minor_parts INTEGER NOT NULL DEFAULT 0,
            completions INTEGER NOT NULL DEFAULT 0,
            rating REAL,
            start_date REAL NOT NULL,
            end_date REAL)"""
        sql_staff_mapping = """CREATE TABLE IF NOT EXISTS consumable_staff(
                            staff_id INTEGER NOT NULL,
                            consumable_id INTEGER NOT NULL,
                            role TEXT,
                            PRIMARY KEY (staff_id, consumable_id)
                            FOREIGN KEY (staff_id)
                                REFERENCES staff (id)
                                ON DELETE CASCADE
                                ON UPDATE NO ACTION
                            FOREIGN KEY (consumable_id)
                                REFERENCES consumables (id)
                                ON DELETE CASCADE
                                ON UPDATE NO ACTION
                            )"""
        cls._get_db().cursor().execute(sql)
        cls._get_db().cursor().execute(sql_staff_mapping)

    @classmethod
    def staff_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS staff(
            id INTEGER PRIMARY KEY NOT NULL,
            first_name TEXT,
            last_name TEXT,
            pseudonym TEXT)"""
        cls._get_db().cursor().execute(sql)