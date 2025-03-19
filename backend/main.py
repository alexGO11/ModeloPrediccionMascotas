from fastapi import FastAPI
from router.router import test
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origin = [
    'http://frontend:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(test)