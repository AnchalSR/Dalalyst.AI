from fastapi import APIRouter, Depends, HTTPException, Query

from agents.radar_agent import RadarAgent
from auth.dependencies import get_current_user
from models.schemas import AuthenticatedUser, PortfolioStockRequest
from services.portfolio_service import PortfolioService
from services.radar_service import OpportunityRadarService
from services.stock_service import StockDataError

router = APIRouter()
radar_agent = RadarAgent()
radar_service = OpportunityRadarService()
portfolio_service = PortfolioService()


@router.get("/watchlist")
async def watchlist():
    return {"symbols": radar_service.stock_service.parse_symbols(None)}


@router.get("/analyze")
async def analyze_symbol(symbol: str = Query(..., description="NSE ticker such as RELIANCE or RELIANCE.NS")):
    try:
        return radar_agent.analyze(symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/alerts")
async def get_alerts(
    symbols: str | None = Query(None, description="Comma-separated symbols"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    parsed_symbols = symbols.split(",") if symbols else None
    return radar_agent.scan(parsed_symbols, user_id=current_user.id)


@router.get("/saved")
async def saved_alerts(current_user: AuthenticatedUser = Depends(get_current_user)):
    return {"alerts": radar_service.get_saved_alerts(current_user.id)}


@router.get("/portfolio")
async def get_portfolio(current_user: AuthenticatedUser = Depends(get_current_user)):
    return radar_agent.portfolio(current_user.id)


@router.post("/portfolio")
async def add_portfolio_stock(
    payload: PortfolioStockRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        stocks = portfolio_service.add_stock(current_user.id, payload.stock)
        return {"stocks": stocks}
    except StockDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/portfolio/{stock}")
async def remove_portfolio_stock(
    stock: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        stocks = portfolio_service.remove_stock(current_user.id, stock)
        return {"stocks": stocks}
    except StockDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
