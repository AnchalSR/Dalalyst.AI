from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import math

import pandas as pd
import yfinance as yf


DEFAULT_WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
]

INDIAN_STOCK_SUGGESTIONS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "AXISBANK.NS",
]

COMMON_NON_INDIAN_SYMBOLS = {
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "GOOG",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
}


class StockDataError(RuntimeError):
    """Raised when market data cannot be loaded."""


@dataclass(slots=True)
class StockService:
    def normalize_symbol(self, symbol: str) -> str:
        normalized = symbol.strip().upper()
        if not normalized:
            raise StockDataError("Stock symbol is required.")
        if " " in normalized:
            raise StockDataError("Use a valid Indian stock symbol like RELIANCE or RELIANCE.NS.")

        if "." in normalized:
            if not normalized.endswith(".NS"):
                raise StockDataError(
                    "Only Indian NSE symbols are supported. Use symbols like RELIANCE or RELIANCE.NS."
                )
            base_symbol = normalized[:-3]
        else:
            base_symbol = normalized

        if base_symbol in COMMON_NON_INDIAN_SYMBOLS:
            raise StockDataError(
                "Non-Indian stocks are not supported. Use NSE symbols like RELIANCE, TCS, or INFY."
            )

        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        if not base_symbol or len(base_symbol) > 12 or any(char not in allowed_chars for char in base_symbol):
            raise StockDataError("Invalid Indian stock format. Enter an NSE symbol like TCS or TCS.NS.")

        return f"{base_symbol}.NS"

    def parse_symbols(self, symbols: list[str] | None) -> list[str]:
        if not symbols:
            return DEFAULT_WATCHLIST
        cleaned = [self.normalize_symbol(symbol) for symbol in symbols if symbol.strip()]
        return cleaned or DEFAULT_WATCHLIST

    def get_snapshot(self, symbol: str, period: str = "6mo") -> dict:
        normalized = self.normalize_symbol(symbol)
        fetch_error = None
        try:
            ticker = yf.Ticker(normalized)
            history = ticker.history(period=period, interval="1d", auto_adjust=False)
        except Exception as exc:
            fetch_error = exc
            history = pd.DataFrame()

        if history.empty:
            if self._should_use_demo_fallback(fetch_error) or self._can_use_empty_history_fallback(normalized):
                return self._build_demo_snapshot(normalized)
            if fetch_error is not None:
                raise StockDataError(
                    f"Failed to load live market data for {normalized}. Please try again later."
                ) from fetch_error
            raise StockDataError(f"No market data found for {normalized}. Check the ticker symbol and try again.")

        history = history.dropna(subset=["Close", "Volume"]).copy()
        if history.empty:
            raise StockDataError(f"{normalized} returned empty price or volume data.")
        history["SMA20"] = history["Close"].rolling(window=20).mean()
        history["SMA50"] = history["Close"].rolling(window=50).mean()
        dates = pd.to_datetime(history.index)
        if getattr(dates, "tz", None) is not None:
            dates = dates.tz_localize(None)
        history["Date"] = dates

        current_close = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else current_close
        current_volume = int(history["Volume"].iloc[-1])
        avg_volume = float(history["Volume"].tail(20).mean())
        sma20 = float(history["SMA20"].iloc[-1]) if pd.notna(history["SMA20"].iloc[-1]) else current_close
        sma50 = float(history["SMA50"].iloc[-1]) if pd.notna(history["SMA50"].iloc[-1]) else current_close

        info = {}
        try:
            info = ticker.info or {}
        except Exception:
            info = {}

        name = info.get("shortName") or info.get("longName") or normalized
        series = []
        for _, row in history.tail(180).iterrows():
            series.append(
                {
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                    "sma20": round(float(row["SMA20"]), 2) if pd.notna(row["SMA20"]) else None,
                    "sma50": round(float(row["SMA50"]), 2) if pd.notna(row["SMA50"]) else None,
                }
            )

        return {
            "symbol": normalized,
            "name": name,
            "current_price": round(current_close, 2),
            "previous_close": round(previous_close, 2),
            "change_percent": round(((current_close - previous_close) / previous_close) * 100, 2)
            if previous_close
            else 0.0,
            "current_volume": current_volume,
            "average_volume": round(avg_volume, 2),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "high_52w": round(float(history["High"].tail(252).max()), 2),
            "low_52w": round(float(history["Low"].tail(252).min()), 2),
            "history": series,
            "data_source": "live",
        }

    def _should_use_demo_fallback(self, error: Exception | None) -> bool:
        if error is None:
            return False
        message = str(error).lower()
        return (
            "query1.finance.yahoo.com" in message
            or "query2.finance.yahoo.com" in message
            or "winerror 10013" in message
            or "failed to establish a new connection" in message
        )

    def _can_use_empty_history_fallback(self, symbol: str) -> bool:
        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.")
        return bool(symbol) and len(symbol) <= 15 and all(char in allowed_chars for char in symbol)

    def _build_demo_snapshot(self, symbol: str) -> dict:
        seed = int(hashlib.sha256(symbol.encode("utf-8")).hexdigest()[:8], 16)
        base_price = 80 + (seed % 220)
        slope = ((seed % 11) - 5) * 0.35
        wave = 4 + (seed % 7)
        today = date.today()

        history = []
        previous_close = base_price
        for days_ago in range(180, 0, -1):
            session_date = today - timedelta(days=days_ago)
            trend_component = slope * (180 - days_ago)
            cycle_component = math.sin((180 - days_ago) / 8) * wave
            close = max(12, base_price + trend_component + cycle_component)
            open_price = close - math.sin((180 - days_ago) / 5) * 1.2
            high = max(open_price, close) + 1.8
            low = min(open_price, close) - 1.6
            volume = int(900000 + (seed % 300000) + (abs(cycle_component) * 65000))
            history.append(
                {
                    "date": session_date.strftime("%Y-%m-%d"),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": volume,
                    "sma20": None,
                    "sma50": None,
                }
            )
            previous_close = close

        closes = [item["close"] for item in history]
        for index, item in enumerate(history):
            last_20 = closes[max(0, index - 19) : index + 1]
            last_50 = closes[max(0, index - 49) : index + 1]
            item["sma20"] = round(sum(last_20) / len(last_20), 2)
            item["sma50"] = round(sum(last_50) / len(last_50), 2)

        current_price = history[-1]["close"]
        prior_close = history[-2]["close"]
        avg_volume = round(sum(item["volume"] for item in history[-20:]) / 20, 2)

        return {
            "symbol": symbol,
            "name": f"{symbol} Demo Feed",
            "current_price": round(current_price, 2),
            "previous_close": round(prior_close, 2),
            "change_percent": round(((current_price - prior_close) / prior_close) * 100, 2),
            "current_volume": history[-1]["volume"],
            "average_volume": avg_volume,
            "sma20": history[-1]["sma20"],
            "sma50": history[-1]["sma50"],
            "high_52w": round(max(item["high"] for item in history), 2),
            "low_52w": round(min(item["low"] for item in history), 2),
            "history": history,
            "data_source": "demo_fallback",
        }

    def build_market_profile(self, snapshot: dict) -> dict:
        history = snapshot["history"]
        latest = history[-1]
        month_ago = history[-21] if len(history) >= 21 else history[0]
        one_month_change = (
            round(((latest["close"] - month_ago["close"]) / month_ago["close"]) * 100, 2)
            if month_ago["close"]
            else 0.0
        )
        volume_ratio = (
            round(snapshot["current_volume"] / snapshot["average_volume"], 2)
            if snapshot["average_volume"]
            else 0.0
        )
        price_vs_sma20_pct = (
            round(((snapshot["current_price"] - snapshot["sma20"]) / snapshot["sma20"]) * 100, 2)
            if snapshot["sma20"]
            else 0.0
        )
        price_vs_sma50_pct = (
            round(((snapshot["current_price"] - snapshot["sma50"]) / snapshot["sma50"]) * 100, 2)
            if snapshot["sma50"]
            else 0.0
        )

        if (
            snapshot["current_price"] > snapshot["sma20"] > snapshot["sma50"]
            and one_month_change > 0
        ):
            trend = "uptrend"
        elif (
            snapshot["current_price"] < snapshot["sma20"] < snapshot["sma50"]
            and one_month_change < 0
        ):
            trend = "downtrend"
        else:
            trend = "sideways"

        return {
            "trend": trend,
            "one_month_change": one_month_change,
            "volume_ratio": volume_ratio,
            "price_vs_sma20_pct": price_vs_sma20_pct,
            "price_vs_sma50_pct": price_vs_sma50_pct,
        }

    def build_context(self, snapshot: dict) -> str:
        profile = self.build_market_profile(snapshot)
        return (
            f"Symbol: {snapshot['symbol']}\n"
            f"Company: {snapshot['name']}\n"
            "Market: Indian equities (NSE)\n"
            f"Current Price: {snapshot['current_price']}\n"
            f"Daily Change: {snapshot['change_percent']}%\n"
            f"SMA20: {snapshot['sma20']}\n"
            f"SMA50: {snapshot['sma50']}\n"
            f"Current Volume: {snapshot['current_volume']}\n"
            f"Average Volume (20d): {snapshot['average_volume']}\n"
            f"Volume Ratio: {profile['volume_ratio']}x\n"
            f"Trend Direction: {profile['trend']}\n"
            f"1-Month Change: {profile['one_month_change']}%\n"
            f"Price vs SMA20: {profile['price_vs_sma20_pct']}%\n"
            "Market Notes: Consider NSE trading behavior, sector leadership, and FII/DII participation.\n"
            f"52-Week High: {snapshot['high_52w']}\n"
            f"52-Week Low: {snapshot['low_52w']}"
        )
