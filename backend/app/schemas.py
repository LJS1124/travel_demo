from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    destination: str = Field(min_length=1, description="目的地城市")
    days: int = Field(ge=1, le=15, description="出行天数")
    travelers: int = Field(ge=1, le=20, description="出行人数")
    budget_cny: float = Field(gt=0, description="预算（人民币）")
    preferences: list[str] = Field(default_factory=list, description="偏好标签")


class HealthResponse(BaseModel):
    status: str
    service: str

