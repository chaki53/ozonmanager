from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_auth import router as auth_router

app = FastAPI(title="Ozon Manager API")

ALLOWED = ["https://ruw.dgy2.ru"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(auth_router)
