from consumption.consumption_backend.Consumable import Consumable
from consumption.consumption_backend.Database import SQLiteDatabaseHandler, SQLiteTableInstantiator
import sqlite3
import unittest

db = sqlite3.connect("testdb.db")
SQLiteDatabaseHandler.DB_CONNECTION = db
SQLiteTableInstantiator.DB_CONNECTION = db

class TestConsumable(unittest.TestCase):

    def setUp(self) -> None:
        SQLiteTableInstantiator.consumable_table()

    def tearDown(self) -> None:
        db.cursor().execute("DROP TABLE IF EXISTS consumables")

    def test_save(self):
        cons = Consumable(name="To Kill a Mockingbird", type="Novel")
        id = cons.save()
        self.assertIsNotNone(id)
        get_cons = Consumable.get(id)
        self.assertEqual(cons, get_cons)
    
    def test_get(self):
        cons = Consumable(name="Minecraft: Guide to Redstone", type="Guide")
        id = cons.save()
        get_cons = Consumable.get(id)
        self.assertEqual(cons, get_cons)

    def test_find(self):
        # Found conss
        fcons1 = Consumable(name="It", completions=3, rating=5.3, type="Movie")
        fcons1.id = fcons1.save()
        fcons2 = Consumable(name="The Stand", completions=3, rating=5.3, type="Novel")
        fcons2.id = fcons2.save()
        fcons3 = Consumable(name="The Shining", completions=3, rating=5.3, type="Movie")
        fcons3.id = fcons3.save()
        # Unfound conss
        cons = Consumable(name="Misery", completions=3, rating=5.2, type="Film")
        cons.save()
        cons = Consumable(name="Carrie", completions=0, rating=5.3, type="Film")
        cons.save()
        find_conss = Consumable.find(completions=3, rating=5.3)
        f_conss = [fcons1, fcons2, fcons3]
        self.assertTrue(len(find_conss) == len(f_conss))
        for cons in f_conss:
            self.assertIn(cons, find_conss)

if __name__ == '__main__':
    unittest.main()