from services.radar_service import OpportunityRadarService


class RadarAgent:
    def __init__(self):
        self.service = OpportunityRadarService()

    def analyze(self, symbol: str) -> dict:
        return self.service.analyze_symbol(symbol)

    def scan(self, symbols: list[str] | None, user_id: int | None = None) -> dict:
        return self.service.scan_watchlist(symbols, user_id=user_id)

    def portfolio(self, user_id: int) -> dict:
        return self.service.get_portfolio_snapshot(user_id)
