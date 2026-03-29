from fastapi import APIRouter, Depends, HTTPException, Query

from agents.chat_agent import ChatAgent
from auth.dependencies import get_current_user
from models.schemas import AuthenticatedUser, ChatRequest
from services.stock_service import StockDataError

router = APIRouter()
chat_agent = ChatAgent()


@router.post("/message")
async def send_message(
    payload: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        return chat_agent.reply(current_user.id, payload.message, payload.symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/history")
async def history(
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return {"messages": chat_agent.history(current_user.id, limit)}
