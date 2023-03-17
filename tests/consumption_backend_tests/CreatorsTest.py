import consumption.consumption_backend.Creators as crea
from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import sqlite3
import unittest

SQLiteDatabaseHandler.DB_CONNECTION = sqlite3.connect("testdb.db")

class TestAuthor(unittest.TestCase):

    def drop_auth_table(self):
        SQLiteDatabaseHandler.get_db().cursor().execute("DROP TABLE IF EXISTS authors")

    def test_save(self):
        self.drop_auth_table()
        author = crea.Author(first_name="John", last_name="Doe", pseudonym="SavedAuthor")
        id = author.save()
        author.id = id
        self.assertIsNotNone(id)
        get_author = crea.Author.get(id)
        self.assertEqual(author, get_author)
    
    def test_get(self):
        self.drop_auth_table()
        author = crea.Author(first_name="Mary", last_name="Jane", pseudonym="GetAuthor")
        id = author.save()
        author.id = id
        get_author = crea.Author.get(id)
        self.assertEqual(author, get_author)

    def test_find(self):
        self.drop_auth_table()
        # Found Authors
        fauthor1 = crea.Author(first_name="Max", last_name="Imum", pseudonym="FoundAuthor")
        fauthor1.id = fauthor1.save()
        fauthor2 = crea.Author(first_name="Max", last_name="LastName", pseudonym="FoundAuthor")
        fauthor2.id = fauthor2.save()
        fauthor3 = crea.Author(first_name="Max", last_name="Imum", pseudonym="FoundAuthor")
        fauthor3.id = fauthor3.save()
        # Unfound Authors
        author = crea.Author(first_name="Max", last_name="Imum", pseudonym="UnfoundAuthor")
        author.save()
        author = crea.Author(first_name="Min", last_name="Imum", pseudonym="TestAuthor")
        author.save()
        find_authors = crea.Author.find(author_first_name="Max", author_pseudonym="FoundAuthor")
        f_authors = [fauthor1, fauthor2, fauthor3]
        self.assertTrue(len(find_authors) == len(f_authors))
        for author in f_authors:
            self.assertIn(author, find_authors)

if __name__ == '__main__':
    unittest.main()