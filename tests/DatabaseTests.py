from consumption.consumption_backend.Database import SQLiteDatabaseHandler
import unittest
import sqlite3

db = sqlite3.connect("testdb.db")
SQLiteDatabaseHandler.DB_CONNECTION = db

class TestSQLiteDatabaseHandler(unittest.TestCase):

    def setUp(self) -> None:
        db.cursor().execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY NOT NULL, value TEXT)")
    
    def tearDown(self) -> None:
        db.cursor().execute("DROP TABLE test")
        
    def test_insert_findone(self):
        input = "Hello World!"
        SQLiteDatabaseHandler.insert("test", id=101, value=input)
        result = SQLiteDatabaseHandler.find_one("test", id=101)
        self.assertTrue(result[0] == 101 and result[1] == input)
    
    def test_insert_findmany(self):
        input = "Same Value"
        SQLiteDatabaseHandler.insert("test", id=1001, value=input)
        SQLiteDatabaseHandler.insert("test", id=1002, value=input)
        SQLiteDatabaseHandler.insert("test", id=1003, value=input)
        result = SQLiteDatabaseHandler.find_many("test", value=input)
        for i, res in enumerate(result):
            with self.subTest(i=i):
                self.assertTrue(res[1] == input)
        self.assertEqual(len(result), 3)

    def test_insert_update_one(self):
        input = "ABCD"
        SQLiteDatabaseHandler.insert("test", id=2001, value=input)
        SQLiteDatabaseHandler.insert("test", id=2002, value=input)
        SQLiteDatabaseHandler.insert("test", id=2003, value=input)
        SQLiteDatabaseHandler.update("test", dict({"value" : "EFGH"}), id=2001)
        result = SQLiteDatabaseHandler.find_many("test", value="EFGH")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 2001)
        self.assertEqual(result[0][1], "EFGH")

    def test_insert_update_many(self):
        input = "ZXCV"
        SQLiteDatabaseHandler.insert("test", id=3001, value=input)
        SQLiteDatabaseHandler.insert("test", id=3002, value=input)
        SQLiteDatabaseHandler.insert("test", id=3003, value=input)
        SQLiteDatabaseHandler.update("test", dict({"value" : "VBNM"}), value=input)
        result = SQLiteDatabaseHandler.find_many("test", value="VBNM")
        self.assertEqual(len(result), 3)

    def test_insert_delete_one(self):
        input = "DeleteOneInput"
        SQLiteDatabaseHandler.insert("test", id=4001, value=input)
        SQLiteDatabaseHandler.insert("test", id=4002, value=input)
        SQLiteDatabaseHandler.insert("test", id=4003, value=input)
        self.assertTrue(SQLiteDatabaseHandler.delete("test", id=4002))
        result = SQLiteDatabaseHandler.find_many("test", value=input)
        self.assertEqual(len(result), 2)
        for i, res in enumerate(result):
            with self.subTest(i=i):
                self.assertTrue(res[0] != 4002)

    def test_insert_delete_many(self):
        input = "DeleteManyInput"
        SQLiteDatabaseHandler.insert("test", id=5001, value=input)
        SQLiteDatabaseHandler.insert("test", id=5002, value=input)
        SQLiteDatabaseHandler.insert("test", id=5003, value="OtherInputLol")
        self.assertTrue(SQLiteDatabaseHandler.delete("test", value=input))
        result = SQLiteDatabaseHandler.find_many("test", value=input)
        self.assertEqual(len(result), 0)
        result = SQLiteDatabaseHandler.find_one("test", id=5003)
        self.assertEqual(result[0], 5003)

if __name__ == '__main__':
    unittest.main()