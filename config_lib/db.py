from pymongo import MongoClient, errors


class MongoDBHandler:
    def __init__(self, mongo_uri, db_name, collection_name="configs"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except errors.ConnectionFailure as exc:
            raise RuntimeError(f"Could not connect to MongoDB: {exc}") from exc

    def save_config(self, name, config):
        try:
            result = self.collection.update_one(
                {"name": name},
                {"$set": {"name": name, "config": config}},
                upsert=True,
            )

            if result.upserted_id:
                print(f"Configuration saved as new document with name: '{name}'")
            elif result.modified_count > 0:
                print(f"Configuration updated successfully for name: '{name}'")
            else:
                print(f"Configuration already up-to-date for name: '{name}'")

            return result
        except errors.PyMongoError as exc:
            raise RuntimeError(f"MongoDB save error: {exc}") from exc

    def load_config(self, name):
        try:
            doc = self.collection.find_one({"name": name})
            if not doc:
                raise ValueError(f"No configuration found with name '{name}'")

            print(f"Configuration loaded successfully for name: '{name}'")

            return doc["config"]
        except errors.PyMongoError as exc:
            raise RuntimeError(f"MongoDB load error: {exc}") from exc

    def delete_config(self, name):
        try:
            result = self.collection.delete_one({"name": name})

            if result.deleted_count == 0:
                print(f"No configuration found with name '{name}' to delete")
            else:
                print(f"Configuration with name '{name}' deleted successfully")

            return result.deleted_count
        except errors.PyMongoError as exc:
            raise RuntimeError(f"MongoDB delete error: {exc}") from exc
