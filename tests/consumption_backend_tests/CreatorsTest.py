import consumption.consumption_backend.Creators as crea
from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import sqlite3
import unittest

SQLiteDatabaseHandler.DB_CONNECTION = sqlite3.connect("testdb.db")

class TestAuthor(unittest.TestCase):

    def test_save(self):
        author = crea.Author(None, "John", "Doe", "SavedAuthor")
        id = author.save()
        print(crea.Author.get(id))
    
    def test_get(self):
        author = crea.Author(None, "Mary", "Jane", "GetAuthor")
        id = author.save()
        print(crea.Author.get(id))

    def test_find(self):
        author = crea.Author(None, "Max", "Imum", "FoundAuthor")
        author.save()
        print(crea.Author.find(author_first_name="Max", author_pseudonym="FoundAuthor"))

if __name__ == '__main__':
    unittest.main()