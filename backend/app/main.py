from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_auth import router as auth_router
from app.api.routes_sync import router as sync_router
from app.api.routes_reports import router as reports_router
from app.api.routes_accounts import router as accounts_router
from app.api.routes_dashboard import router as dashboard_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(sync_router)
app.include_router(reports_router)
app.include_router(dashboard_router)

@app.get("/healthz")
def healthz():
    return {"ok": True}
