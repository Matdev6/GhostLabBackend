from fastapi import FastAPI
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.models import beats  # ou onde estiver o model Beats
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Monta os arquivos estáticos
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


beats.Base.metadata.create_all(bind=engine)

# CORS para permitir chamadas do frontend (caso tenha)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
