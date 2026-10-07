from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.init_db import create_tables, ensure_initial_manager
from app.routers import admin, auth, datasets, quality_checks


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    ensure_initial_manager()
    yield


app = FastAPI(title="Catalogue API", lifespan=lifespan)

# L'authentification passe par l'en-tête Authorization (pas de cookies) :
# pas besoin d'allow_credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(quality_checks.router)
app.include_router(admin.router)
