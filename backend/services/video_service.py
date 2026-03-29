from services.ai_service import AIServiceError, GroqService
from services.chart_service import ChartIntelligenceService
from services.radar_service import OpportunityRadarService
from services.stock_service import StockService


class VideoEngineService:
    def __init__(self):
        self.stock_service = StockService()
        self.radar_service = OpportunityRadarService()
        self.chart_service = ChartIntelligenceService()
        self.groq_service = GroqService()

    def generate_script(self, symbol: str) -> dict:
        snapshot = self.stock_service.get_snapshot(symbol)
        radar = self.radar_service.analyze_symbol(symbol)
        chart = self.chart_service.analyze_symbol(symbol)

        payload = self._generate_ai_slides(snapshot, radar, chart)
        slides = payload.get("slides") if isinstance(payload, dict) else None
        if not isinstance(slides, list) or not slides:
            slides = self._fallback_slides(snapshot, radar, chart)

        return {
            "symbol": snapshot["symbol"],
            "name": snapshot["name"],
            "summary": radar["explanation"],
            "slides": slides,
        }

    def _generate_ai_slides(self, snapshot: dict, radar: dict, chart: dict) -> dict:
        try:
            return self.groq_service.generate_json(
                system_prompt=(
                    "You create concise investor video storyboards in strict JSON for Indian equities only. "
                    "Use NSE market context, sector positioning, and investor-focused language."
                ),
                user_prompt=(
                    "Create an Indian stock summary video script as JSON with the shape "
                    '{"slides":[{"title":"", "bullets":["",""], "narration":"", "visual":""}]}.\n\n'
                    f"{self.stock_service.build_context(snapshot)}\n"
                    f"Radar recommendation: {radar['recommendation']}\n"
                    f"Radar explanation: {radar['explanation']}\n"
                    f"Chart trend: {chart['trend']}\n"
                    f"Chart summary: {chart['summary']}"
                ),
            )
        except (AIServiceError, ValueError):
            return {}

    def _fallback_slides(self, snapshot: dict, radar: dict, chart: dict) -> list[dict]:
        return [
            {
                "title": f"{snapshot['symbol']} in 30 seconds",
                "bullets": [
                    f"Current price: Rs {snapshot['current_price']}",
                    f"Daily move: {snapshot['change_percent']}%",
                    f"Recommendation: {radar['recommendation']}",
                ],
                "narration": f"{snapshot['name']} is currently trading at Rs {snapshot['current_price']}, and the radar module rates it {radar['recommendation']}.",
                "visual": "Hero chart with latest price and ticker badge",
            },
            {
                "title": "Opportunity radar",
                "bullets": [
                    radar["signal_summary"],
                    f"Volume today: {radar['metrics']['current_volume']}",
                    f"Average volume: {radar['metrics']['average_volume']}",
                ],
                "narration": radar["explanation"],
                "visual": "Signal icons for breakout and volume confirmation",
            },
            {
                "title": "Chart intelligence",
                "bullets": [
                    f"Trend: {chart['trend']}",
                    f"Support: Rs {chart['support']}",
                    f"Resistance: Rs {chart['resistance']}",
                ],
                "narration": chart["summary"],
                "visual": "Annotated line chart with support and resistance",
            },
            {
                "title": "Investor checklist",
                "bullets": [
                    "Confirm follow-through volume on the next sessions",
                    "Watch price behavior around support and resistance",
                    "Manage risk if the breakout fails",
                ],
                "narration": "Use the signal as a starting point, not as a blind instruction. Confirm price action and size risk appropriately.",
                "visual": "Checklist card with risk controls",
            },
        ]
