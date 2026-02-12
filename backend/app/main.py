import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .plan_service import generate_plan
from .schemas import HealthResponse, PlanRequest


def _cors_origins() -> list[str]:
    origins = os.environ.get("CORS_ALLOW_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500")
    return [item.strip() for item in origins.split(",") if item.strip()]


app = FastAPI(
    title="Travel SaaS MVP API",
    version="0.2.0",
    description="旅游规划 MVP 后端服务（FastAPI）",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="travel-saas-mvp")


@app.post("/api/plan")
def create_plan(payload: PlanRequest) -> dict[str, Any]:
    return generate_plan(payload.model_dump())
