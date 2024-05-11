from fastapi import FastAPI, HTTPException, Response, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from datetime import timedelta
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

router = FastAPI()

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
    "https://blueberry.adefe.xyz",
    "https://api.blueberry.adefe.xyz",
    "http://localhost:8192",
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
def post_recipe(value: RecipeForUI, request: Request):
    """
    Upload new recipe in raw JSON format (authentification required)
    """
    logging.info(f"POST /recipe")

    token = request.cookies.get("blueberry-token", None)
    if token is None:
        logging.info("No token")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No token specified")

    user = request.cookies.get("blueberry-user", None)
    if user is None:
        logging.info("No user detected")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No user specified")

    if not mariadb.check_token(user, token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token is bad")

    logging.info(f"Detected user: {user} has OK token")

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
            register_result_token = mariadb.register(data.login, data.password)
        except LoginTakenError as exc:
            logging.info(f"Cannot register, this user exists")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Login is taken"
            )
        response.set_cookie(
            "blueberry-token",
            register_result_token,
            httponly=True,
            expires=timedelta(days=1),
            domain="blueberry.adefe.xyz",
        )
        response.set_cookie(
            "blueberry-user",
            data.login,
            httponly=False,
            expires=timedelta(days=1),
            domain="blueberry.adefe.xyz",
        )
        logging.info(f"Registered, user: {data.login}")
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
        auth_result_token = mariadb.authentificate_user(data.login, data.password)
        if auth_result_token:
            response.set_cookie(
                "blueberry-token",
                auth_result_token,
                httponly=True,
                expires=timedelta(days=1),
                domain="blueberry.adefe.xyz",
            )

            response.set_cookie(
                "blueberry-user",
                data.login,
                httponly=False,
                expires=timedelta(days=1),
                domain="blueberry.adefe.xyz",
            )
            logging.info(f"Login success, user: {data.login}")
            response.status_code = status.HTTP_200_OK
            return response
        logging.info(f"Wrong login data")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except MariaDBError as exc:
        logging.info(f"Cannot login: {exc.args}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
