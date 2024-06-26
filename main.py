from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.routes import users, auth, product_category, prices, products, favorites, favorite_items, baskets, \
    basket_items, images, product_sub_category, reviews, orders, cooperation, posts, ukr_poshta, nova_poshta

import logging
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from src.conf.logging_config import setup_logging
from src.services.scheduler_tasks import start_scheduler, stop_scheduler
from src.services.sentry import sentry_sdk

setup_logging()


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SentryAsgiMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", description='Main page')
def root():
    """
    Main page definition

    :return: dict: health status

    """
    logger.info("User accessed the main page")
    return {"message": "Welcome to the FastAPI Store!"}


@app.get("/error")
async def error_endpoint():
    try:
        raise ValueError("This is a sample error that will be logged to Sentry.")
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise e


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    Health Checker

    :param db: database session
    :return: dict: health status
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        logger.info("User accessed the healthchecker page")
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(product_category.router, prefix='/api')
app.include_router(product_sub_category.router, prefix='/api')
app.include_router(products.router, prefix='/api')
app.include_router(prices.router, prefix='/api')
app.include_router(favorites.router, prefix='/api')
app.include_router(favorite_items.router, prefix='/api')
app.include_router(baskets.router, prefix='/api')
app.include_router(basket_items.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(reviews.router, prefix='/api')
app.include_router(orders.router, prefix='/api')
app.include_router(cooperation.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(ukr_poshta.router, prefix='/api')
app.include_router(nova_poshta.router, prefix='/api')
