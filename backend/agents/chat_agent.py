from services.chat_service import MarketChatService


class ChatAgent:
    def __init__(self):
        self.service = MarketChatService()

    def reply(self, user_id: int, message: str, symbol: str | None = None) -> dict:
        return self.service.send_message(user_id=user_id, message=message, symbol=symbol)

    def history(self, user_id: int, limit: int = 20) -> list[dict]:
        return self.service.get_history(user_id=user_id, limit=limit)
