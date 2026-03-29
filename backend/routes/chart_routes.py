from fastapi import APIRouter, HTTPException, Query

from agents.chart_agent import ChartAgent
from services.stock_service import StockDataError

router = APIRouter()
chart_agent = ChartAgent()


@router.get("/analyze")
async def analyze_chart(symbol: str = Query(..., description="NSE ticker such as RELIANCE or RELIANCE.NS")):
    try:
        return chart_agent.analyze(symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
