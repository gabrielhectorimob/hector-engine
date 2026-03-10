from app.schemas.brain import BrainResult
from app.engines.engine_executor import EngineExecutor


class HectorResponseOrchestrator:

    def __init__(self):
        self.executor = EngineExecutor()

    def build_answer(self, result: BrainResult, question: str):

        engine_output = self.executor.execute(
            result.routing,
            question
        )

        return {
            "mode": "engine_execution",
            "question": question,
            "brain": {
                "question_type": result.classification.question_type,
                "domain": result.classification.domain,
                "intent": result.intent.intent,
                "route": result.routing.route,
                "target_engine": result.routing.target_engine,
                "execution_mode": result.execution_plan.execution_mode,
                "steps": result.execution_plan.steps
            },
            "engine_output": engine_output
        }
