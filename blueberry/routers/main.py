from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import time
from models.recipe_models import (
    RecipeList,
    RecipeForUI,
)
from modules.mongo_connector import MongoConnector, MongoError


router = FastAPI()
mongo = MongoConnector()

logging.basicConfig(
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(
            f"/app/logs/log_{time.ctime().replace(' ', '_')}.txt",
            mode="w",
            encoding="UTF-8",
        )
    ],
    datefmt="%H:%M:%S UTC",
    level=logging.INFO,
)

origins = [
    "*",
]

router.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DESCRIPTION = """
Blueberry is an automated cooking book which 
tells you exactly how to cook! 🚀
"""


def custom_openapi():
    """
    Custom OpenAPI docs
    """
    if router.openapi_schema:
        return router.openapi_schema
    openapi_schema = get_openapi(
        title="Blueberry🫐",
        version="0.0.1",
        description=DESCRIPTION,
        routes=router.routes,
        contact={
            "name": "Blueberry GitHub",
            "url": "https://github.com/Adefey/blueberry_backend",
        },
    )
    router.openapi_schema = openapi_schema
    return router.openapi_schema


router.openapi = custom_openapi


@router.get("/recipe/all", response_model=RecipeList)
def get_all(count: int = 20, offset: int = 0, search_query: str = None):
    """
    Get all recipes
    """
    logging.info("GET /recipe/all")
    try:
        data = mongo.get_all(offset, count, search_query)
        total = mongo.count()
    except MongoError as exc:
        logging.error(f"Cannot get data: {exc.args}")
        raise HTTPException(500, detail={"error": f"{exc.args}"}) from exc
    logging.info(f"Collected data: {data}, total: {total}")
    return RecipeList(recipes=data, total=total)


@router.get("/recipe/{id}", response_model=RecipeForUI)
def get_by_id(id: int):
    """
    Get recipe by ID
    """
    logging.info(f"GET /recipe/{id}")
    try:
        data = mongo.get(id)
    except MongoError as exc:
        logging.error(f"Cannot get data: {exc.args}")
        raise HTTPException(500, detail={"error": f"{exc.args}"}) from exc
    logging.info(f"Collected data: {data}")
    return data


@router.post("/recipe", response_model=int)
def post_recipe(value: RecipeForUI):
    """
    Upload new recipe in raw JSON format
    """
    logging.info(f"POST /recipe")
    try:
        id = mongo.set(value)
    except MongoError as exc:
        logging.error(f"Cannot upload data: {exc.args}")
        raise HTTPException(500, detail={"error": f"{exc.args}"}) from exc
    logging.info(f"Created, given _id: {id}")
    return id
