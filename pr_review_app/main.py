from fastapi import FastAPI
from pr_review_app.api.pr_review_routes import router
from shared.db.init_db import init_db
import shared.logging_config  # noqa: F401


app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    init_db() 

app.include_router(router) 