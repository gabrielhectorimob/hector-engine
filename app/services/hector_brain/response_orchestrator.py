from app.schemas.brain import BrainResult


class HectorResponseOrchestrator:
    """
    Monta a resposta final institucional da Fase 1.
    Nesta etapa, o Brain já opera como orquestrador real.
    """

    def build_answer(self, result: BrainResult, question: str) -> str:
        return (
            "HECTOR BRAIN — ORQUESTRAÇÃO INICIAL ATIVA\n\n"
            f"Pergunta recebida: {question}\n"
            f"Tipo identificado: {result.classification.question_type}\n"
            f"Domínio identificado: {result.classification.domain}\n"
            f"Intenção identificada: {result.intent.intent}\n"
            f"Rota semântica: {result.routing.route}\n"
            f"Motor-alvo: {result.routing.target_engine}\n"
            f"Modo de execução: {result.execution_plan.execution_mode}\n\n"
            "Status: o Hector Brain classificou a pergunta com sucesso e definiu "
            "o plano institucional de execução. Nesta Fase 1, o sistema ainda "
            "não executa motores especialistas reais; ele estabelece a camada "
            "profissional de decisão semântica que servirá de base para os "
            "motores financeiros, comerciais, urbanísticos e de planilhas."
        )
