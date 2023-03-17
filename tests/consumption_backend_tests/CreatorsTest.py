import consumption.consumption_backend.Creators as crea
from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import sqlite3
import unittest

SQLiteDatabaseHandler.DB_CONNECTION = sqlite3.connect("testdb.db")

class TestAuthor(unittest.TestCase):

    def drop_auth_table(self):
        SQLiteDatabaseHandler.get_db().cursor().execute("DROP TABLE authors")

    def test_save(self):
        self.drop_auth_table()
        author = crea.Author(None, "John", "Doe", "SavedAuthor")
        id = author.save()
        author.id = id
        self.assertIsNotNone(id)
        get_author = crea.Author.get(id)
        self.assertEqual(author, get_author)
    
    def test_get(self):
        self.drop_auth_table()
        author = crea.Author(None, "Mary", "Jane", "GetAuthor")
        id = author.save()
        author.id = id
        get_author = crea.Author.get(id)
        self.assertEqual(author, get_author)

    def test_find(self):
        self.drop_auth_table()
        # Found Authors
        fauthor1 = crea.Author(None, "Max", "Imum", "FoundAuthor")
        fauthor1.id = fauthor1.save()
        fauthor2 = crea.Author(None, "Max", "LastName", "FoundAuthor")
        fauthor2.id = fauthor2.save()
        fauthor3 = crea.Author(None, "Max", "Imum", "FoundAuthor")
        fauthor3.id = fauthor3.save()
        # Unfound Authors
        author = crea.Author(None, "Max", "Imum", "UnfoundAuthor")
        author.save()
        author = crea.Author(None, "Min", "Imum", "TestAuthor")
        author.save()
        find_authors = crea.Author.find(author_first_name="Max", author_pseudonym="FoundAuthor")
        f_authors = [fauthor1, fauthor2, fauthor3]
        self.assertTrue(len(find_authors) == len(f_authors))
        for author in f_authors:
            self.assertIn(author, find_authors)

if __name__ == '__main__':
    unittest.main()