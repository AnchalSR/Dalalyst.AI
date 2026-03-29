from database import get_db
from services.portfolio_service import PortfolioService
from services.radar_service import OpportunityRadarService
from services.ai_service import AIServiceError, GroqService
from services.stock_service import StockService


class MarketChatService:
    def __init__(self):
        self.stock_service = StockService()
        self.groq_service = GroqService()
        self.portfolio_service = PortfolioService()
        self.radar_service = OpportunityRadarService()

    def send_message(self, user_id: int, message: str, symbol: str | None = None) -> dict:
        context_block = "No symbol-specific context provided."
        normalized_symbol = None
        portfolio_context = self.portfolio_service.build_context(user_id)
        portfolio_signal_context = self._build_portfolio_signal_context(user_id)
        if symbol:
            normalized_symbol = self.stock_service.normalize_symbol(symbol)
            snapshot = self.stock_service.get_snapshot(normalized_symbol)
            context_block = self.stock_service.build_context(snapshot)

        history = self.get_history(user_id, limit=6)
        reply = self._generate_reply(
            message,
            context_block,
            history,
            portfolio_context,
            portfolio_signal_context,
        )

        with get_db() as connection:
            cursor = connection.execute(
                """
                INSERT INTO chats (user_id, symbol, message, response)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, normalized_symbol, message, reply),
            )
            row = connection.execute(
                "SELECT id, symbol, message, response, timestamp FROM chats WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

        return {"reply": reply, "saved_message": dict(row)}

    def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        with get_db() as connection:
            rows = connection.execute(
                """
                SELECT id, symbol, message, response, timestamp
                FROM chats
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def _generate_reply(
        self,
        message: str,
        context_block: str,
        history: list[dict],
        portfolio_context: str,
        portfolio_signal_context: str,
    ) -> str:
        prior_turns = []
        for item in history[-4:]:
            prior_turns.append(f"User: {item['message']}")
            prior_turns.append(f"Assistant: {item['response']}")
        history_block = "\n".join(prior_turns) or "No prior conversation."

        fallback = (
            "Groq is unavailable right now, so here is a deterministic Indian-market investor response. "
            f"Use the NSE stock context to judge trend, price versus moving averages, and whether volume confirms the move. "
            f"Question: {message}"
        )

        try:
            return self.groq_service.generate_text(
                system_prompt=(
                    "Answer user queries only in the context of Indian equities listed on NSE. "
                    "Be precise, context-aware, and investor-focused. Avoid generic disclaimers. "
                    "Refer to the supplied stock context directly. Include Indian market behavior such as sector rotation, "
                    "FII/DII flows, and NSE price action when relevant. If the data is insufficient, say exactly what is missing."
                ),
                user_prompt=(
                    f"Conversation so far:\n{history_block}\n\n"
                    f"Stock context:\n{context_block}\n\n"
                    f"Portfolio context:\n{portfolio_context}\n\n"
                    f"Portfolio signal summary:\n{portfolio_signal_context}\n\n"
                    f"User query:\n{message}\n\n"
                    "Respond with three short sections: View, Why, Risks/Next Check. "
                    "If relevant, mention portfolio stocks with the strongest signal or clearest risk. "
                    "Stay within the Indian market context and do not discuss US-listed stocks."
                ),
                max_tokens=500,
            )
        except AIServiceError:
            return fallback

    def _build_portfolio_signal_context(self, user_id: int) -> str:
        stocks = self.portfolio_service.list_stocks(user_id)
        if not stocks:
            return "No portfolio signal context available."

        summaries = []
        for stock in stocks[:5]:
            try:
                analysis = self.radar_service.analyze_symbol(stock)
                summaries.append(
                    f"{stock}: {analysis['recommendation']} | {analysis['signal_strength']} | confidence {analysis['confidence_score']}/100"
                )
            except Exception:
                continue

        return "\n".join(summaries) if summaries else "No portfolio signal context available."
