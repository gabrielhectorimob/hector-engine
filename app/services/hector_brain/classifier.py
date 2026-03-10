from app.schemas.brain import BrainClassification


class HectorQuestionClassifier:
    """
    Classifica a natureza da pergunta.
    Esta primeira versão é determinística e institucional.
    Não tenta 'responder'; apenas classifica.
    """

    def classify(self, question: str) -> BrainClassification:
        q = question.lower().strip()

        indicator_keywords = [
            "vgv", "vpl", "tir", "xtir", "mtir", "lucro", "margem",
            "preço", "valor", "ticket", "receita", "custo", "indice", "índice"
        ]

        explanation_keywords = [
            "explique", "explica", "o que é", "conceito", "defina", "significa"
        ]

        comparison_keywords = [
            "compare", "comparar", "diferença", "versus", "vs", "melhor que", "pior que"
        ]

        simulation_keywords = [
            "simule", "simular", "cenário", "projeção", "projetar"
        ]

        diagnosis_keywords = [
            "diagnóstico", "diagnosticar", "problema", "erro", "falha", "por que"
        ]

        if any(keyword in q for keyword in simulation_keywords):
            return BrainClassification(
                question_type="simulation",
                domain=self._detect_domain(q),
                confidence=0.92
            )

        if any(keyword in q for keyword in comparison_keywords):
            return BrainClassification(
                question_type="comparison",
                domain=self._detect_domain(q),
                confidence=0.91
            )

        if any(keyword in q for keyword in explanation_keywords):
            return BrainClassification(
                question_type="explanation",
                domain=self._detect_domain(q),
                confidence=0.93
            )

        if any(keyword in q for keyword in diagnosis_keywords):
            return BrainClassification(
                question_type="diagnostic",
                domain=self._detect_domain(q),
                confidence=0.89
            )

        if any(keyword in q for keyword in indicator_keywords):
            return BrainClassification(
                question_type="indicator_query",
                domain=self._detect_domain(q),
                confidence=0.94
            )

        return BrainClassification(
            question_type="general_query",
            domain=self._detect_domain(q),
            confidence=0.70
        )

    def _detect_domain(self, question: str) -> str:
        financial_keywords = [
            "vgv", "vpl", "tir", "xtir", "mtir", "lucro", "margem",
            "receita", "custo", "caixa", "payback", "desconto"
        ]

        commercial_keywords = [
            "venda", "vendas", "absorção", "velocidade", "ticket", "cliente", "mercado"
        ]

        urban_keywords = [
            "área", "area", "lote", "lotes", "densidade", "zoneamento", "gleba", "quadra"
        ]

        spreadsheet_keywords = [
            "planilha", "aba", "coluna", "linha", "excel", "tabela", "célula", "celula"
        ]

        if any(keyword in question for keyword in financial_keywords):
            return "financial"

        if any(keyword in question for keyword in commercial_keywords):
            return "commercial"

        if any(keyword in question for keyword in urban_keywords):
            return "urban"

        if any(keyword in question for keyword in spreadsheet_keywords):
            return "spreadsheet"

        return "project"
