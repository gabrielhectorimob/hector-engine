from app.engines.financial_engine import FinancialEngine
from app.knowledge.real_estate_kb import RealEstateKnowledgeBase


class EngineExecutor:

    def __init__(self):

        self.financial_engine = FinancialEngine()
        self.kb = RealEstateKnowledgeBase()

    def execute(self, routing, question: str):

        if routing.target_engine == "financial_engine":

            example_cashflow = [
                -2500000,
                0,
                0,
                0,
                2555722,
                100593,
                100593,
                100593
            ]

            result = self.financial_engine.evaluate_project(
                example_cashflow,
                0.015
            )

            return {
                "engine": "financial_engine",
                "result": result
            }

        return {
            "engine": "fallback",
            "result": "engine not implemented"
        }
