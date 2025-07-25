from fastapi import FastAPI
from fastapi_app.api.pr_review_routes import router

app = FastAPI()

app.include_router(router) 