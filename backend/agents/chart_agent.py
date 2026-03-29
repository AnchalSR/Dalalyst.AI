from services.chart_service import ChartIntelligenceService


class ChartAgent:
    def __init__(self):
        self.service = ChartIntelligenceService()

    def analyze(self, symbol: str) -> dict:
        return self.service.analyze_symbol(symbol)
