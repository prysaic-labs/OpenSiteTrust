from pydantic import BaseModel, Field
from typing import Any, List, Optional, Literal, Dict

Label = Literal["safe", "suspicious", "danger"]


Breakdown = Dict[str, float]


class SiteScore(BaseModel):
    host: str
    score: float
    level: Literal["green", "amber", "red"]
    breakdown: Breakdown
    updated_at: str
    votes_total: int | None = None
    u_included: bool | None = None


class Signal(BaseModel):
    key: str
    value: Any | None = None
    effect: Optional[str] = None


class Explanation(BaseModel):
    host: str
    model_version: str = Field(default="v0.1")
    signals: List[Signal]


class VoteRequest(BaseModel):
    host: str
    label: Label
    reason: Optional[str] = None
    user: Optional[str] = None  # TODO: replace with JWT user in real impl


class VoteResponse(BaseModel):
    ok: bool
    new_score: float
