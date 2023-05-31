import consumption.consumption_backend.Consumables as cons
from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import sqlite3
import unittest

SQLiteDatabaseHandler.DB_CONNECTION = sqlite3.connect("testdb.db")

class TestNovel(unittest.TestCase):

    def drop_novel_table(self):
        SQLiteDatabaseHandler.get_db().cursor().execute("DROP TABLE IF EXISTS novels")

    def test_save(self):
        self.drop_novel_table()
        novel = cons.Novel(name="To Kill a Mockingbird")
        id = novel.save()
        novel.id = id
        self.assertIsNotNone(id)
        get_novel = cons.Novel.get(id)
        self.assertEqual(novel, get_novel)
    
    def test_get(self):
        self.drop_novel_table()
        novel = cons.Novel(name="Minecraft: Guide to Redstone")
        id = novel.save()
        novel.id = id
        get_novel = cons.Novel.get(id)
        self.assertEqual(novel, get_novel)

    def test_find(self):
        self.drop_novel_table()
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
        find_novels = cons.Novel.find(nov_completions=3, nov_rating=5.3)
        f_novels = [fnovel1, fnovel2, fnovel3]
        self.assertTrue(len(find_novels) == len(f_novels))
        for novel in f_novels:
            self.assertIn(novel, find_novels)

if __name__ == '__main__':
    unittest.main()