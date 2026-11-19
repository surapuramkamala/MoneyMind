from pydantic import BaseModel, Field


class AdvisorRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    year: int = Field(ge=2000, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)


class AdvisorResponse(BaseModel):
    answer: str
    year: int
    month: int | None
    provider: str = "NVIDIA NIM"