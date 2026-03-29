from fastapi import APIRouter, Depends, HTTPException, Query

from agents.video_agent import VideoAgent
from auth.dependencies import get_current_user
from models.schemas import AuthenticatedUser
from services.stock_service import StockDataError

router = APIRouter()
video_agent = VideoAgent()


@router.get("/generate")
async def generate_video(
    symbol: str = Query(..., description="NSE ticker such as RELIANCE or RELIANCE.NS"),
    _: AuthenticatedUser = Depends(get_current_user),
):
    try:
        return video_agent.generate(symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
