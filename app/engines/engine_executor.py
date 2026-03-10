from app.engines.financial_engine import FinancialEngine
from app.knowledge.real_estate_kb import RealEstateKnowledgeBase


class EngineExecutor:

    def __init__(self):

        self.financial_engine = FinancialEngine()
        self.kb = RealEstateKnowledgeBase()

    def execute(self, routing, question: str):

        if routing.target_engine == "financial_engine":

            # fluxo exemplo temporário até integração com planilha
            cashflow = [
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
                cashflow,
                0.015
            )

            context = {
                "benchmark_price": self.kb.get_benchmark_price("espirito_santo_litoral"),
                "expected_sales_velocity": self.kb.get_expected_sales_velocity("loteamento_premium"),
                "market_context": self.kb.market_context()
            }

            return {
                "engine": "financial_engine",
                "execution_mode": "real_engine",
                "question": question,
                "result": result,
                "context": context
            }

        return {
            "engine": "fallback",
            "execution_mode": "none",
            "question": question,
            "result": "engine not implemented"
        }
