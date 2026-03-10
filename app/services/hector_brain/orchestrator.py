from app.schemas.brain import BrainResult
from app.services.hector_brain.classifier import HectorQuestionClassifier
from app.services.hector_brain.execution_planner import HectorExecutionPlanner
from app.services.hector_brain.intent_detector import HectorIntentDetector
from app.services.hector_brain.response_orchestrator import HectorResponseOrchestrator
from app.services.hector_brain.semantic_router import HectorSemanticRouter


class HectorBrainOrchestrator:
    """
    Orquestrador central do Hector Brain.
    Regra arquitetural:
    - Brain decide
    - Motores executam
    - LLM apoia
    """

    def __init__(self) -> None:
        self.classifier = HectorQuestionClassifier()
        self.intent_detector = HectorIntentDetector()
        self.router = HectorSemanticRouter()
        self.planner = HectorExecutionPlanner()
        self.response_orchestrator = HectorResponseOrchestrator()

    def process(self, question: str) -> BrainResult:
        classification = self.classifier.classify(question)
        intent = self.intent_detector.detect(question)
        routing = self.router.route(classification, intent)
        execution_plan = self.planner.build_plan(classification, intent, routing)

        result = BrainResult(
            classification=classification,
            intent=intent,
            routing=routing,
            execution_plan=execution_plan,
            final_answer="",
        )

        final_answer = self.response_orchestrator.build_answer(result, question)

        return BrainResult(
            classification=classification,
            intent=intent,
            routing=routing,
            execution_plan=execution_plan,
            final_answer=final_answer,
        )
