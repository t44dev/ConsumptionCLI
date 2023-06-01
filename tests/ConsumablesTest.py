import consumption.consumption_backend.Consumables as cons
from consumption.consumption_backend.Database import SQLiteDatabaseHandler, SQLiteTableInstantiator
import sqlite3
import unittest

db = sqlite3.connect("testdb.db")
SQLiteDatabaseHandler.DB_CONNECTION = db
SQLiteTableInstantiator.DB_CONNECTION = db


class TestNovel(unittest.TestCase):

    def reset_novel_table(self):
        db.cursor().execute("DROP TABLE IF EXISTS novels")
        SQLiteTableInstantiator.novel_table()

    def test_save(self):
        self.reset_novel_table()
        novel = cons.Novel(name="To Kill a Mockingbird")
        id = novel.save()
        novel.id = id
        self.assertIsNotNone(id)
        get_novel = cons.Novel.get(id)
        self.assertEqual(novel, get_novel)
    
    def test_get(self):
        self.reset_novel_table()
        novel = cons.Novel(name="Minecraft: Guide to Redstone")
        id = novel.save()
        novel.id = id
        get_novel = cons.Novel.get(id)
        self.assertEqual(novel, get_novel)

    def test_find(self):
        self.reset_novel_table()
        # Found Novels
        fnovel1 = cons.Novel(name="It", completions=3, rating=5.3)
        fnovel1.id = fnovel1.save()
        fnovel2 = cons.Novel(name="The Stand", completions=3, rating=5.3)
        fnovel2.id = fnovel2.save()
        fnovel3 = cons.Novel(name="The Shining", completions=3, rating=5.3)
        fnovel3.id = fnovel3.save()
        # Unfound Novels
        novel = cons.Novel(name="Misery", completions=3, rating=5.2)
        novel.save()
        novel = cons.Novel(name="Carrie", completions=0, rating=5.3)
        novel.save()
        find_novels = cons.Novel.find(completions=3, rating=5.3)
        f_novels = [fnovel1, fnovel2, fnovel3]
        self.assertTrue(len(find_novels) == len(f_novels))
        for novel in f_novels:
            self.assertIn(novel, find_novels)

if __name__ == '__main__':
    unittest.main()