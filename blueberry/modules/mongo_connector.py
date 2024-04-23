from pymongo import MongoClient

from models.recipe_models import (
    RecipeForList,
    RecipeForUI,
    StepForUI,
)

from modules.config import (
    MONGO_PORT,
    MONGO_USER,
    MONGO_PASSWORD,
    MONGO_DB,
)


class MongoError(RuntimeError):
    pass


class MongoConnector:

    def __init__(self):
        CONNECTION_STRING = (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@mongo:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
        )
        client = MongoClient(CONNECTION_STRING)
        self.client_db = client["blueberry"]
        self.collection = self.client_db["recipes"]
        ###
        example = RecipeForUI(steps=[StepForUI(), StepForUI()])
        self.collection.insert_one(example.model_dump())
        ###

    def get(self, id: str) -> RecipeForUI:
        try:
            value = self.collection.find_one({"id": id})
        except Exception as exc:
            raise TypeError from exc
        return RecipeForUI.model_validate(value)

    def get_all(self) -> list[RecipeForList]:
        try:
            values = [
                RecipeForUI.model_validate(value) for value in self.collection.find()
            ]
        except Exception as exc:
            raise TypeError from exc
        return values

    def set(self, value: RecipeForUI) -> int:
        try:
            inserted_id = self.collection.insert_one(value.model_dump()).inserted_id
        except Exception as exc:
            raise TypeError from exc
        return inserted_id

    def count(self) -> int:
        try:
            count =  self.collection.count_documents({})
        except Exception as exc:
            raise TypeError from exc
        return count
