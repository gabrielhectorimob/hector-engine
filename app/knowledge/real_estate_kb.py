from typing import Dict, List


class RealEstateKnowledgeBase:

    def get_benchmark_price(self, region: str) -> float:

        benchmarks: Dict[str, float] = {
            "espirito_santo_litoral": 900.0,
            "espirito_santo_interior": 350.0,
            "sul_bahia_litoral": 700.0
        }

        return benchmarks.get(region, 500.0)

    def get_expected_sales_velocity(self, project_type: str) -> float:

        velocity: Dict[str, float] = {
            "loteamento_premium": 0.08,
            "loteamento_padrao": 0.05,
            "condominio_fechado": 0.04
        }

        return velocity.get(project_type, 0.05)

    def market_context(self) -> Dict[str, object]:

        return {
            "segment": "loteamentos",
            "focus": "premium coastal developments",
            "primary_buyers": [
                "empresarios",
                "medicos",
                "advogados",
                "investidores"
            ]
        }
