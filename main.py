import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.conf.config import settings
from src.database.db import get_db
from src.routes import users, auth, product_category, prices, products, favorites, favorite_items, baskets, basket_items

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


sentry_sdk.init(
    dsn=settings.sentry_url,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI()

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
    return {"message": "Welcome to the FastAPI Store!"}


@app.get("/error")
async def error_endpoint():
    raise ValueError("This is a sample error that will be logged to Sentry.")


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
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(product_category.router, prefix='/api')
app.include_router(products.router, prefix='/api')
app.include_router(prices.router, prefix='/api')
app.include_router(favorites.router, prefix='/api')
app.include_router(favorite_items.router, prefix='/api')
app.include_router(baskets.router, prefix='/api')
app.include_router(basket_items.router, prefix='/api')
