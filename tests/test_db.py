import unittest
from unittest.mock import MagicMock, patch
from pymongo import errors
from config_lib.db import MongoDBHandler


class TestMongoDBHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client_patch = patch("config_lib.db.MongoClient")
        self.mock_client = self.mock_client_patch.start()
        self.addCleanup(self.mock_client_patch.stop)

        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()

        self.mock_client.return_value.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection

        self.handler = MongoDBHandler("mongodb://test", "testdb", "testcoll")

    def test_connection_success(self):
        self.assertEqual(self.handler.db, self.mock_db)
        self.assertEqual(self.handler.collection, self.mock_collection)

    def test_connection_failure(self):
        with patch("config_lib.db.MongoClient", side_effect=errors.ConnectionFailure("Connection error")):
            with self.assertRaises(RuntimeError) as cm:
                MongoDBHandler("mongodb://invalid", "db")

            self.assertIn("Could not connect to MongoDB", str(cm.exception))

    def test_save_config_new(self):
        self.mock_collection.update_one.return_value = MagicMock(upserted_id="123", modified_count=0)
        result = self.handler.save_config("config1", {"a": 1})

        self.mock_collection.update_one.assert_called_once_with(
            {"name": "config1"},
            {"$set": {"name": "config1", "config": {"a": 1}}},
            upsert=True,
        )
        self.assertEqual(result.upserted_id, "123")

    def test_save_config_updated(self):
        self.mock_collection.update_one.return_value = MagicMock(upserted_id=None, modified_count=1)
        result = self.handler.save_config("config2", {"b": 2})
        self.assertEqual(result.modified_count, 1)

    def test_save_config_no_change(self):
        self.mock_collection.update_one.return_value = MagicMock(upserted_id=None, modified_count=0)
        result = self.handler.save_config("config3", {"c": 3})
        self.assertEqual(result.modified_count, 0)

    def test_save_config_pymongo_error(self):
        self.mock_collection.update_one.side_effect = errors.PyMongoError("Save failed")
        with self.assertRaises(RuntimeError) as cm:
            self.handler.save_config("bad_config", {"fail": True})
        self.assertIn("MongoDB save error", str(cm.exception))

    def test_load_config_success(self):
        expected = {"name": "config1", "config": {"x": 42}}
        self.mock_collection.find_one.return_value = expected
        config = self.handler.load_config("config1")
        self.assertEqual(config, expected["config"])

    def test_load_config_not_found(self):
        self.mock_collection.find_one.return_value = None
        with self.assertRaises(ValueError):
            self.handler.load_config("unknown")

    def test_load_config_pymongo_error(self):
        self.mock_collection.find_one.side_effect = errors.PyMongoError("Load failed")
        with self.assertRaises(RuntimeError) as cm:
            self.handler.load_config("bad_load")
        self.assertIn("MongoDB load error", str(cm.exception))

    def test_delete_config_success(self):
        self.mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        deleted_count = self.handler.delete_config("config1")
        self.assertEqual(deleted_count, 1)

    def test_delete_config_not_found(self):
        self.mock_collection.delete_one.return_value = MagicMock(deleted_count=0)
        deleted_count = self.handler.delete_config("nonexistent")
        self.assertEqual(deleted_count, 0)

    def test_delete_config_pymongo_error(self):
        self.mock_collection.delete_one.side_effect = errors.PyMongoError("Delete failed")
        with self.assertRaises(RuntimeError) as cm:
            self.handler.delete_config("bad_delete")
        self.assertIn("MongoDB delete error", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
