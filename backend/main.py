from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from router.test_routes import test_routes
from router.post_codes_routes import post_codes_routes
from router.auth_routes import auth_routes
from router.aemet_routes import aemet_routes
from router.human_routes import human_routes

app = FastAPI()
scheduler = AsyncIOScheduler()

app.add_middleware(
    CORSMiddleware,
    #allow_origins=[
    #    "http://localhost:3000",  # Para frontend local
    #    "http://localhost:80",    # Si accedes desde el navegador con Nginx
    #    "http://app:80",          # Para frontend dentro de Docker
    #    "http://app:3000"         # Para frontend dentro de Docker
    #],
    
    allow_origins=["http://localhost",
                   "https://localhost"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(test_routes, prefix="/api/test", tags=["test"])
app.include_router(post_codes_routes, prefix="/api/post_codes", tags=["post_codes"])
app.include_router(auth_routes, prefix="/api/auth", tags=["auth"])
app.include_router(aemet_routes, prefix="/api/aemet", tags=["aemet"])
app.include_router(human_routes, prefix="/api/human", tags=["human"])