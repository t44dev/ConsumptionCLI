import consumption.consumption_backend.Consumables as cons
from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import sqlite3

SQLiteDatabaseHandler.DB_CONNECTION = sqlite3.connect("testdb.db")

