from app.schemas.brain import BrainIntent


class HectorIntentDetector:
    """
    Detecta a intenção operacional da pergunta.
    """

    def detect(self, question: str) -> BrainIntent:
        q = question.lower().strip()

        if any(word in q for word in ["calcular", "calc", "quanto", "valor", "resultado"]):
            return BrainIntent(intent="calculate", confidence=0.93)

        if any(word in q for word in ["analisar", "análise", "avaliar", "diagnóstico"]):
            return BrainIntent(intent="analyze", confidence=0.92)

        if any(word in q for word in ["compare", "comparar", "diferença", "vs", "versus"]):
            return BrainIntent(intent="compare", confidence=0.94)

        if any(word in q for word in ["explique", "explica", "o que é", "conceito", "defina"]):
            return BrainIntent(intent="explain", confidence=0.95)

        if any(word in q for word in ["simule", "simular", "cenário", "projeção", "projetar"]):
            return BrainIntent(intent="simulate", confidence=0.94)

        if any(word in q for word in ["buscar", "localize", "encontre", "mostre"]):
            return BrainIntent(intent="retrieve", confidence=0.88)

        return BrainIntent(intent="understand", confidence=0.70)
