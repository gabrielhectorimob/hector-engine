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

        return (
            "HECTOR ENGINE — EXECUÇÃO REAL ATIVA\n\n"
            f"Pergunta: {question}\n"
            f"Domínio: {result.classification.domain}\n"
            f"Motor selecionado: {result.routing.target_engine}\n\n"
            f"Resultado do motor: {engine_output}"
        )
