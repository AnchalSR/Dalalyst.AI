from database import get_db
from services.portfolio_service import PortfolioService
from services.ai_service import AIServiceError, GroqService
from services.stock_service import StockDataError, StockService


class OpportunityRadarService:
    def __init__(self):
        self.stock_service = StockService()
        self.groq_service = GroqService()
        self.portfolio_service = PortfolioService()

    def analyze_symbol(self, symbol: str) -> dict:
        snapshot = self.stock_service.get_snapshot(symbol)
        profile = self.stock_service.build_market_profile(snapshot)
        scoring = self._score_signal(snapshot, profile)
        explanation = self._build_explanation(snapshot, profile, scoring)
        why_this_matters = self._build_why_this_matters(snapshot, profile, scoring)
        risk_alerts = self._build_risk_alerts(snapshot, profile)
        historical_accuracy = self._calculate_historical_accuracy(snapshot)
        estimated_impact = self._estimate_impact(historical_accuracy)
        risk_factors = self._build_risk_factors(snapshot, profile, risk_alerts)

        return {
            "symbol": snapshot["symbol"],
            "name": snapshot["name"],
            "current_price": snapshot["current_price"],
            "change_percent": snapshot["change_percent"],
            "signals": scoring["signals"],
            "signal_summary": scoring["signal_summary"],
            "signal_strength": scoring["signal_strength"],
            "recommendation": scoring["recommendation"],
            "confidence": scoring["confidence_label"],
            "confidence_score": scoring["confidence_score"],
            "historical_accuracy": historical_accuracy,
            "estimated_impact": estimated_impact,
            "explanation": explanation,
            "why_this_matters": why_this_matters,
            "risk_factors": risk_factors,
            "risk_alerts": risk_alerts,
            "history": snapshot["history"],
            "metrics": {
                "sma20": snapshot["sma20"],
                "sma50": snapshot["sma50"],
                "current_volume": snapshot["current_volume"],
                "average_volume": snapshot["average_volume"],
                "volume_ratio": profile["volume_ratio"],
                "trend": profile["trend"],
                "one_month_change": profile["one_month_change"],
                "price_vs_sma20_pct": profile["price_vs_sma20_pct"],
            },
            "score_breakdown": scoring["score_breakdown"],
        }

    def scan_watchlist(self, symbols: list[str] | None, user_id: int | None = None) -> dict:
        alerts = []
        errors = []
        for symbol in self.stock_service.parse_symbols(symbols):
            try:
                analysis = self.analyze_symbol(symbol)
                alerts.append(analysis)
                if user_id is not None:
                    self._store_alert(user_id, analysis)
            except StockDataError as exc:
                errors.append({"symbol": symbol, "error": str(exc)})

        priority = {"BUY": 0, "WATCH": 1, "AVOID": 2}
        alerts.sort(
            key=lambda item: (
                priority[item["recommendation"]],
                -item["confidence_score"],
                item["symbol"],
            )
        )

        return {
            "alerts": alerts,
            "risk_alerts": self._collect_risk_alerts(alerts),
            "errors": errors,
            "summary": {
                "buy": sum(item["recommendation"] == "BUY" for item in alerts),
                "watch": sum(item["recommendation"] == "WATCH" for item in alerts),
                "avoid": sum(item["recommendation"] == "AVOID" for item in alerts),
            },
        }

    def get_portfolio_snapshot(self, user_id: int) -> dict:
        stocks = self.portfolio_service.list_stocks(user_id)
        if not stocks:
            return {
                "stocks": [],
                "alerts": [],
                "risk_alerts": [],
                "opportunity_summary": "Add portfolio stocks to generate personalized insights.",
            }

        analyses = []
        errors = []
        for stock in stocks:
            try:
                analyses.append(self.analyze_symbol(stock))
            except StockDataError as exc:
                errors.append({"symbol": stock, "error": str(exc)})

        opportunities = [item for item in analyses if item["recommendation"] in {"BUY", "WATCH"}]
        top_pick = max(opportunities, key=lambda item: item["confidence_score"], default=None)
        summary = (
            f"{len(opportunities)} of {len(analyses)} portfolio stocks show actionable setups."
            if analyses
            else "Portfolio data is unavailable right now."
        )
        if top_pick:
            summary += f" Best current opportunity: {top_pick['symbol']} with {top_pick['signal_strength']} at {top_pick['confidence_score']}/100 confidence."

        return {
            "stocks": stocks,
            "alerts": analyses,
            "risk_alerts": self._collect_risk_alerts(analyses),
            "errors": errors,
            "opportunity_summary": summary,
        }

    def get_saved_alerts(self, user_id: int, limit: int = 25) -> list[dict]:
        with get_db() as connection:
            rows = connection.execute(
                """
                SELECT id, stock, signal, recommendation, created_at
                FROM alerts
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

        return [dict(row) for row in rows]

    def _store_alert(self, user_id: int, analysis: dict) -> None:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO alerts (user_id, stock, signal, recommendation) VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    analysis["symbol"],
                    analysis["signal_summary"],
                    analysis["recommendation"],
                ),
            )

    def _score_signal(self, snapshot: dict, profile: dict) -> dict:
        price_change = snapshot["change_percent"]
        volume_ratio = profile["volume_ratio"]
        trend = profile["trend"]

        if price_change >= 4:
            price_score = 35
        elif price_change >= 2:
            price_score = 28
        elif price_change >= 1:
            price_score = 20
        elif price_change >= 0:
            price_score = 10
        else:
            price_score = 3

        if volume_ratio >= 2.5:
            volume_score = 35
        elif volume_ratio >= 1.8:
            volume_score = 28
        elif volume_ratio >= 1.3:
            volume_score = 20
        elif volume_ratio >= 1.0:
            volume_score = 10
        else:
            volume_score = 3

        trend_score_map = {"uptrend": 30, "sideways": 15, "downtrend": 5}
        trend_score = trend_score_map[trend]

        raw_score = price_score + volume_score + trend_score
        confidence_score = max(5, min(99, raw_score))

        if confidence_score >= 75:
            signal_strength = "Strong Breakout"
            recommendation = "BUY"
            confidence_label = "High"
        elif confidence_score >= 55:
            signal_strength = "Moderate Breakout"
            recommendation = "WATCH"
            confidence_label = "Medium"
        else:
            signal_strength = "Weak Signal"
            recommendation = "AVOID"
            confidence_label = "Low"

        signals = [
            {
                "type": "Price Momentum",
                "detail": f"Price moved {price_change}% on the session.",
            },
            {
                "type": "Volume Ratio",
                "detail": f"Volume is running at {volume_ratio}x the 20-day average.",
            },
            {
                "type": "Trend Direction",
                "detail": f"The broader setup is currently in a {trend}.",
            },
        ]

        return {
            "signal_strength": signal_strength,
            "recommendation": recommendation,
            "confidence_label": confidence_label,
            "confidence_score": confidence_score,
            "signal_summary": f"{signal_strength} driven by {price_change}% price change, {volume_ratio}x volume, and a {trend}.",
            "signals": signals,
            "score_breakdown": {
                "price_change_score": price_score,
                "volume_score": volume_score,
                "trend_score": trend_score,
                "total": raw_score,
            },
        }

    def _build_explanation(self, snapshot: dict, profile: dict, scoring: dict) -> str:
        fallback = (
            f"{snapshot['symbol']} is showing a {scoring['signal_strength'].lower()} with a confidence score of "
            f"{scoring['confidence_score']}/100. The move is being driven by a {snapshot['change_percent']}% price change, "
            f"{profile['volume_ratio']}x relative volume, and a {profile['trend']} backdrop. "
            f"Investors should treat this as a {scoring['recommendation']} setup and watch for failed follow-through, "
            f"volume fading, or a reversal back under the 20-day average."
        )

        try:
            return self.groq_service.generate_text(
                system_prompt=(
                    "You are an Indian equity market analyst. Give specific, non-generic reasoning for NSE-listed stocks only. "
                    "Always explain the signal, what it means for an investor, and concrete risk factors. "
                    "Reference Indian sector behavior, FII/DII participation, and NSE trading tone when relevant."
                ),
                user_prompt=(
                    "Write a concise investor note with three short paragraphs titled: Signal, Investor Interpretation, Risks. "
                    "Avoid generic commentary.\n\n"
                    f"{self.stock_service.build_context(snapshot)}\n"
                    f"Signal Strength: {scoring['signal_strength']}\n"
                    f"Confidence Score: {scoring['confidence_score']}/100\n"
                    f"Recommendation: {scoring['recommendation']}\n"
                    f"Score Breakdown: {scoring['score_breakdown']}"
                ),
            )
        except AIServiceError:
            return fallback

    def _build_why_this_matters(self, snapshot: dict, profile: dict, scoring: dict) -> str:
        fallback = (
            f"This matters because {snapshot['symbol']} is attracting attention with {profile['volume_ratio']}x normal volume. "
            f"If the move holds above the short-term trend, momentum traders may continue to participate; "
            f"if it fails quickly, the setup can unwind into a false breakout."
        )

        try:
            return self.groq_service.generate_text(
                system_prompt=(
                    "You explain why an NSE stock setup matters to Indian market investors. "
                    "Be concrete about market implication, possible outcomes, sector context, and likely reaction from FII/DII-led flows."
                ),
                user_prompt=(
                    "Answer in 2-3 sentences under the heading 'Why This Matters'. "
                    "Explain the market implication and the most likely bullish and bearish outcomes. "
                    "Do not repeat the same points from the main explanation.\n\n"
                    f"{self.stock_service.build_context(snapshot)}\n"
                    f"Signal Strength: {scoring['signal_strength']}\n"
                    f"Recommendation: {scoring['recommendation']}\n"
                    f"Confidence Score: {scoring['confidence_score']}/100"
                ),
                max_tokens=220,
            )
        except AIServiceError:
            return fallback

    def _build_risk_alerts(self, snapshot: dict, profile: dict) -> list[dict]:
        alerts = []
        if profile["trend"] == "downtrend":
            alerts.append(
                {
                    "type": "Downtrend",
                    "severity": "High",
                    "message": f"{snapshot['symbol']} is below both key moving averages and remains in a downtrend.",
                }
            )
        if snapshot["change_percent"] <= -4:
            alerts.append(
                {
                    "type": "Sudden Drop",
                    "severity": "High",
                    "message": f"{snapshot['symbol']} fell {snapshot['change_percent']}% today, which may signal distribution or adverse news.",
                }
            )
        elif snapshot["change_percent"] <= -2 and profile["volume_ratio"] >= 1.5:
            alerts.append(
                {
                    "type": "Heavy Selling",
                    "severity": "Medium",
                    "message": f"{snapshot['symbol']} is down {snapshot['change_percent']}% on {profile['volume_ratio']}x volume.",
                }
            )
        return alerts

    def _build_risk_factors(self, snapshot: dict, profile: dict, risk_alerts: list[dict]) -> list[str]:
        factors = []
        if profile["trend"] != "uptrend":
            factors.append("Trend support is weak, which raises the chance of a failed breakout.")
        if profile["volume_ratio"] < 1.3:
            factors.append("Volume confirmation is limited, so conviction behind the move may be weak.")
        if snapshot["current_price"] < snapshot["sma20"]:
            factors.append("Price is trading below the 20-day moving average.")
        for alert in risk_alerts:
            factors.append(alert["message"])
        return factors[:4]

    def _calculate_historical_accuracy(self, snapshot: dict) -> dict:
        history = snapshot["history"]
        if len(history) < 45:
            return {
                "success_rate": None,
                "sample_size": 0,
                "average_return_per_signal": None,
                "lookback_sessions": len(history),
                "summary": "Not enough history for validation.",
            }

        current_profile = self.stock_service.build_market_profile(snapshot)
        current_scoring = self._score_signal(snapshot, current_profile)
        comparable_signals = 0
        successful_signals = 0
        realized_returns = []

        start_index = max(20, len(history) - 60)
        end_index = len(history) - 6

        for index in range(start_index, end_index):
            window = history[: index + 1]
            derived_snapshot = self._snapshot_from_history(snapshot, window)
            derived_profile = self.stock_service.build_market_profile(derived_snapshot)
            derived_scoring = self._score_signal(derived_snapshot, derived_profile)

            if derived_scoring["signal_strength"] != current_scoring["signal_strength"]:
                continue

            comparable_signals += 1
            entry_close = history[index]["close"]
            future_window = history[index + 1 : index + 6]
            max_gain = max(((item["high"] - entry_close) / entry_close) * 100 for item in future_window)
            max_drawdown = min(((item["low"] - entry_close) / entry_close) * 100 for item in future_window)

            if derived_scoring["recommendation"] in {"BUY", "WATCH"} and max_gain >= 3:
                successful_signals += 1
                realized_returns.append(round(max_gain, 2))
            elif derived_scoring["recommendation"] == "AVOID" and max_drawdown <= -3:
                successful_signals += 1
                realized_returns.append(round(abs(max_drawdown), 2))

        success_rate = (
            round((successful_signals / comparable_signals) * 100, 1) if comparable_signals else None
        )
        average_return = (
            round(sum(realized_returns) / len(realized_returns), 2) if realized_returns else None
        )
        summary = (
            f"{successful_signals} of {comparable_signals} similar signals reached the validation target within 5 sessions."
            if comparable_signals
            else "No comparable historical setups were found in the last 60 sessions."
        )
        return {
            "success_rate": success_rate,
            "sample_size": comparable_signals,
            "average_return_per_signal": average_return,
            "lookback_sessions": end_index - start_index,
            "summary": summary,
        }

    def _estimate_impact(self, historical_accuracy: dict) -> dict:
        success_rate = historical_accuracy.get("success_rate")
        average_return = historical_accuracy.get("average_return_per_signal")
        sample_size = historical_accuracy.get("sample_size") or 0
        lookback_sessions = historical_accuracy.get("lookback_sessions") or 0

        if success_rate is None or average_return is None or sample_size == 0 or lookback_sessions <= 0:
            return {
                "weekly": None,
                "monthly": None,
                "yearly": None,
                "summary": "Not enough validated history to estimate financial impact.",
            }

        signals_per_week = sample_size / max(1, lookback_sessions / 5)
        expected_return_per_signal = average_return * (success_rate / 100)
        weekly = round(expected_return_per_signal * signals_per_week, 2)
        monthly = round(weekly * 4.33, 2)
        yearly = round(monthly * 12, 2)

        return {
            "weekly": weekly,
            "monthly": monthly,
            "yearly": yearly,
            "summary": (
                f"Based on historical validation, similar setups produced about {average_return}% on winning signals, "
                f"which implies an estimated impact of {weekly}% weekly under comparable conditions."
            ),
        }

    def _snapshot_from_history(self, base_snapshot: dict, window: list[dict]) -> dict:
        closes = [item["close"] for item in window]
        volumes = [item["volume"] for item in window]
        current_price = closes[-1]
        previous_close = closes[-2] if len(closes) > 1 else closes[-1]
        sma20_values = [item["sma20"] for item in window if item["sma20"] is not None]
        sma50_values = [item["sma50"] for item in window if item["sma50"] is not None]
        return {
            "symbol": base_snapshot["symbol"],
            "name": base_snapshot["name"],
            "current_price": current_price,
            "previous_close": previous_close,
            "change_percent": round(((current_price - previous_close) / previous_close) * 100, 2)
            if previous_close
            else 0.0,
            "current_volume": volumes[-1],
            "average_volume": round(sum(volumes[-20:]) / min(len(volumes), 20), 2),
            "sma20": round(sma20_values[-1], 2) if sma20_values else current_price,
            "sma50": round(sma50_values[-1], 2) if sma50_values else current_price,
            "high_52w": max(item["high"] for item in window),
            "low_52w": min(item["low"] for item in window),
            "history": window,
        }

    def _collect_risk_alerts(self, alerts: list[dict]) -> list[dict]:
        collected = []
        for item in alerts:
            for risk in item.get("risk_alerts", []):
                collected.append(
                    {
                        "symbol": item["symbol"],
                        "recommendation": item["recommendation"],
                        "type": risk["type"],
                        "severity": risk["severity"],
                        "message": risk["message"],
                    }
                )
        severity_rank = {"High": 0, "Medium": 1, "Low": 2}
        collected.sort(key=lambda item: (severity_rank.get(item["severity"], 3), item["symbol"]))
        return collected
