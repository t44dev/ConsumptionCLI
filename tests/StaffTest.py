from consumption.consumption_backend.Staff import Staff
from consumption.consumption_backend.Consumable import Consumable
from consumption.consumption_backend.Database import SQLiteDatabaseHandler, SQLiteTableInstantiator
import sqlite3
import unittest

db = sqlite3.connect("testdb.db")
SQLiteDatabaseHandler.DB_CONNECTION = db
SQLiteTableInstantiator.DB_CONNECTION = db

class TestStaff(unittest.TestCase):

    def setUp(self) -> None:
        SQLiteTableInstantiator.staff_table()
        SQLiteTableInstantiator.consumable_table()

    def tearDown(self) -> None:
        db.cursor().execute("DROP TABLE IF EXISTS staff")
        db.cursor().execute("DROP TABLE IF EXISTS consumable_staff")

    def test_save(self):
        author = Staff(first_name="John", last_name="Doe", pseudonym="SavedAuthor")
        id = author.save()
        self.assertIsNotNone(id)
        get_author = Staff.get(id)
        self.assertEqual(author, get_author)
    
    def test_get(self):
        author = Staff(first_name="Mary", last_name="Jane", pseudonym="GetAuthor")
        id = author.save()
        get_author = Staff.get(id)
        self.assertEqual(author, get_author)

    def test_find(self):
        # Found Authors
        fauthor1 = Staff(first_name="Max", last_name="Imum", pseudonym="FoundAuthor")
        fauthor1.id = fauthor1.save()
        fauthor2 = Staff(first_name="Max", last_name="LastName", pseudonym="FoundAuthor")
        fauthor2.id = fauthor2.save()
        fauthor3 = Staff(first_name="Max", last_name="Imum", pseudonym="FoundAuthor")
        fauthor3.id = fauthor3.save()
        # Unfound Authors
        author = Staff(first_name="Max", last_name="Imum", pseudonym="UnfoundAuthor")
        author.save()
        author = Staff(first_name="Min", last_name="Imum", pseudonym="TestAuthor")
        author.save()
        find_authors = Staff.find(first_name="Max", pseudonym="FoundAuthor")
        f_authors = [fauthor1, fauthor2, fauthor3]
        self.assertTrue(len(find_authors) == len(f_authors))
        for author in f_authors:
            self.assertIn(author, find_authors)
    
    def test_consumable_interaction(self):
        author1 = Staff(first_name="John")
        author2 = Staff(first_name="Gabe")
        author3 = Staff(first_name="AAAAAAAA")
        author1.save()
        author2.save()
        author3.save()
        cons = Consumable(name="Book")
        cons.save()
        cons.toggle_staff(author1.id, "Author")
        cons.toggle_staff(author2.id, "Illustrator")
        # 2 toggles should result in no change
        cons.toggle_staff(author3.id, "Fake")
        cons.toggle_staff(author3.id, "Fake")
        for i in range(len(cons.staff)):
            with self.subTest(i=i):
                staff = cons.staff[i]
                self.assertTrue(staff == author1 or staff == author2)
        get_cons = Consumable.get(cons.id)
        for i in range(len(get_cons.staff)):
            with self.subTest(i=i):
                staff = get_cons.staff[i]
                self.assertTrue(staff == author1 or staff == author2)

if __name__ == '__main__':
    unittest.main()