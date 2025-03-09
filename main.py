from fastapi import FastAPI
from router.router import test


app = FastAPI()

app.include_router(test)