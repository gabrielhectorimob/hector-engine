from app.schemas.brain import BrainClassification, BrainIntent, BrainRouting


class HectorSemanticRouter:
    """
    Escolhe o motor-alvo com base em domínio + intenção.
    Nesta fase, os motores ainda são lógicos/virtuais.
    """

    def route(self, classification: BrainClassification, intent: BrainIntent) -> BrainRouting:
        domain = classification.domain

        if domain == "financial":
            return BrainRouting(route="financial_route", target_engine="financial_engine")

        if domain == "commercial":
            return BrainRouting(route="commercial_route", target_engine="commercial_engine")

        if domain == "urban":
            return BrainRouting(route="urban_route", target_engine="urban_engine")

        if domain == "spreadsheet":
            return BrainRouting(route="spreadsheet_route", target_engine="spreadsheet_engine")

        return BrainRouting(route="project_route", target_engine="project_context_engine")
