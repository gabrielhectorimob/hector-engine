from app.schemas.brain import (
    BrainClassification,
    BrainExecutionPlan,
    BrainIntent,
    BrainRouting,
)


class HectorExecutionPlanner:
    """
    Monta o plano institucional de execução.
    Ainda não executa motores reais; apenas define a estratégia.
    """

    def build_plan(
        self,
        classification: BrainClassification,
        intent: BrainIntent,
        routing: BrainRouting,
    ) -> BrainExecutionPlan:
        steps = [
            "receive_user_question",
            "classify_question",
            "detect_intent",
            "route_to_target_engine",
        ]

        if classification.question_type == "indicator_query":
            steps.append("prepare_indicator_response")

        if classification.question_type == "comparison":
            steps.append("prepare_comparison_response")

        if classification.question_type == "simulation":
            steps.append("prepare_simulation_response")

        if classification.question_type == "diagnostic":
            steps.append("prepare_diagnostic_response")

        if intent.intent == "explain":
            steps.append("prepare_explanatory_response")

        steps.append("assemble_institutional_response")

        return BrainExecutionPlan(
            execution_mode="orchestrated_semantic_dispatch",
            steps=steps,
        )
