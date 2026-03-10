from pydantic import BaseModel


class BrainClassification(BaseModel):
    question_type: str
    domain: str
    confidence: float


class BrainIntent(BaseModel):
    intent: str
    confidence: float


class BrainRouting(BaseModel):
    route: str
    target_engine: str


class BrainExecutionPlan(BaseModel):
    execution_mode: str
    steps: list[str]


class BrainResult(BaseModel):
    classification: BrainClassification
    intent: BrainIntent
    routing: BrainRouting
    execution_plan: BrainExecutionPlan
    final_answer: str
