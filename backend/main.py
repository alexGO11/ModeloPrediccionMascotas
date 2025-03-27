from fastapi import FastAPI
from router.router import test
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://app:8080",  # Para el frontend dentro de Docker
        "http://localhost:8080" # Para cuando accedas desde el navegador
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(test)