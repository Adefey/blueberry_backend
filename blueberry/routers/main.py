from fastapi import FastAPI, HTTPException, Response, Depends, status
from fastapi_login import LoginManager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import time
from models.recipe_models import (
    RecipeList,
    RecipeForUI,
)
from models.auth_models import (
    AuthRequestModel,
)
from modules.mongo_connector import MongoConnector, MongoError
from modules.mariadb_connector import MariaDB, MariaDBError, LoginTakenError
from typing import Optional
from modules.utils import (
    validate_string,
)
from modules.config import (
    AUTH_SECRET,
)

router = FastAPI()
login_manager = LoginManager(
    AUTH_SECRET, "/login", use_cookie=True, cookie_name="blueberry-token"
)
mongo = MongoConnector()
mariadb = MariaDB()

logging.basicConfig(
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(
            f"/app/logs/log_{int(time.time())}.txt",
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


@router.get("/recipe/all", response_model=RecipeList, tags=["Recipe storage"])
def get_all(count: int = 10, offset: int = 0, search_query: str = None):
    """
    Get all recipes
    """
    logging.info("GET /recipe/all")
    try:
        data = mongo.get_all(offset, count, search_query)
        total = mongo.count()
    except MongoError as exc:
        logging.error(f"Cannot get data: {exc.args}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": f"{exc.args}"}
        ) from exc
    logging.info(f"Collected data: {data}, total: {total}")
    return RecipeList(recipes=data, total=total)


@router.get(
    "/recipe/{id}", response_model=Optional[RecipeForUI], tags=["Recipe storage"]
)
def get_by_id(id: int):
    """
    Get recipe by ID
    """
    logging.info(f"GET /recipe/{id}")
    try:
        data = mongo.get(id)
    except MongoError as exc:
        logging.error(f"Cannot get data: {exc.args}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": f"{exc.args}"}
        ) from exc
    logging.info(f"Collected data: {data}")
    return data


@router.post("/recipe", response_model=int, tags=["Recipe storage"])
def post_recipe(value: RecipeForUI, user=Depends(login_manager.optional)):
    """
    Upload new recipe in raw JSON format (authentification required)
    """
    logging.info(f"POST /recipe")
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    try:
        id = mongo.set(value)
    except MongoError as exc:
        logging.error(f"Cannot upload data: {exc.args}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": f"{exc.args}"}
        ) from exc
    logging.info(f"Created, given _id: {id}")
    return id


@router.post("/user/register", tags=["Authentification"])
def post_register(data: AuthRequestModel, response: Response):
    """
    Register user and set cookie
    """
    logging.info(f"POST /user/register")
    try:
        if not validate_string(data.login):
            logging.info(f"Login: {data.login} validation error")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login must be longer than 4 symbols, letters, digits and most special symbols allowed",
            )
        if not validate_string(data.password):
            logging.info(f"Password: {data.password} validation error")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password must be longer than 4 symbols, letters, digits and most special symbols allowed",
            )
        try:
            mariadb.register(data.login, data.password)
        except LoginTakenError as exc:
            logging.info(f"Cannot register, this user exists")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Login is taken"
            )
        token = login_manager.create_access_token(data={"user": data.login})
        login_manager.set_cookie(response, token)
        logging.info(f"Registered, given cookie: {token}")
        response.status_code = status.HTTP_200_OK
        return response
    except MariaDBError as exc:
        logging.info(f"Cannot register: {exc.args}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/user/login", tags=["Authentification"])
def post_login(data: AuthRequestModel, response: Response):
    """
    Login and set cookie
    """
    logging.info(f"POST /user/login")
    try:
        if mariadb.check_user(data.login, data.password):
            token = login_manager.create_access_token(data={"user": data.login})
            login_manager.set_cookie(response, token)
            logging.info(f"Login success, given cookie: {token}")
            response.status_code = status.HTTP_200_OK
            return response
        logging.info(f"Wrong login data")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except MariaDBError as exc:
        logging.info(f"Cannot login: {exc.args}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
