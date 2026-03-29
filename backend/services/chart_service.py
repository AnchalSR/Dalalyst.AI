from services.ai_service import AIServiceError, GroqService
from services.stock_service import StockService


class ChartIntelligenceService:
    def __init__(self):
        self.stock_service = StockService()
        self.groq_service = GroqService()

    def analyze_symbol(self, symbol: str) -> dict:
        snapshot = self.stock_service.get_snapshot(symbol)
        profile = self.stock_service.build_market_profile(snapshot)
        history = snapshot["history"]
        trend = profile["trend"]
        support = round(min(point["low"] for point in history[-20:]), 2)
        resistance = round(max(point["high"] for point in history[-20:]), 2)
        summary = self._build_summary(snapshot, trend, support, resistance, profile["one_month_change"])

        return {
            "symbol": snapshot["symbol"],
            "name": snapshot["name"],
            "trend": trend,
            "summary": summary,
            "support": support,
            "resistance": resistance,
            "one_month_change": profile["one_month_change"],
            "chart_data": history,
        }

    def _build_summary(
        self,
        snapshot: dict,
        trend: str,
        support: float,
        resistance: float,
        one_month_change: float,
    ) -> str:
        fallback = (
            f"{snapshot['symbol']} is in a {trend}. "
            f"Support is near Rs {support}, resistance is near Rs {resistance}, "
            f"and the one-month move is {one_month_change}%."
        )
        try:
            return self.groq_service.generate_text(
                system_prompt=(
                    "You explain chart structure for active Indian equity investors in plain English. "
                    "Focus on NSE setup quality, key levels, sector behavior, and what would confirm or weaken the move."
                ),
                user_prompt=(
                    "Summarize this NSE stock chart in 3 concise sentences. Include investor interpretation, Indian market context, and one risk.\n\n"
                    f"{self.stock_service.build_context(snapshot)}\n"
                    f"Trend: {trend}\nSupport: {support}\nResistance: {resistance}\nOne-month move: {one_month_change}%"
                ),
                max_tokens=250,
            )
        except AIServiceError:
            return fallback
