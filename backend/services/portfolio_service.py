from database import get_db
from services.stock_service import StockService


class PortfolioService:
    def __init__(self):
        self.stock_service = StockService()

    def list_stocks(self, user_id: int) -> list[str]:
        with get_db() as connection:
            rows = connection.execute(
                "SELECT stock FROM portfolio WHERE user_id = ? ORDER BY stock ASC",
                (user_id,),
            ).fetchall()
        return [row["stock"] for row in rows]

    def add_stock(self, user_id: int, stock: str) -> list[str]:
        normalized = self.stock_service.normalize_symbol(stock)
        self.stock_service.get_snapshot(normalized)
        with get_db() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO portfolio (user_id, stock) VALUES (?, ?)",
                (user_id, normalized),
            )
        return self.list_stocks(user_id)

    def remove_stock(self, user_id: int, stock: str) -> list[str]:
        normalized = self.stock_service.normalize_symbol(stock)
        with get_db() as connection:
            connection.execute(
                "DELETE FROM portfolio WHERE user_id = ? AND stock = ?",
                (user_id, normalized),
            )
        return self.list_stocks(user_id)

    def build_context(self, user_id: int) -> str:
        stocks = self.list_stocks(user_id)
        if not stocks:
            return "Portfolio is empty."
        return "Portfolio stocks: " + ", ".join(stocks)
