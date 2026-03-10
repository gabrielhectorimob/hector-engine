class RealEstateKnowledgeBase:

    def get_benchmark_price(self, region: str):

        benchmarks = {
            "espirito_santo_litoral": 900,
            "espirito_santo_interior": 350,
            "sul_bahia_litoral": 700
        }

        return benchmarks.get(region, 500)

    def get_expected_sales_velocity(self, project_type: str):

        velocity = {
            "loteamento_premium": 0.08,
            "loteamento_padrao": 0.05,
            "condominio_fechado": 0.04
        }

        return velocity.get(project_type, 0.05)

    def market_context(self):

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
