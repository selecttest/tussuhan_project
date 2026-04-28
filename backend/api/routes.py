from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.dependencies import get_config, get_dashboard_service
from config import Config
from services import DashboardService


router = APIRouter()
DashboardDependency = Annotated[DashboardService, Depends(get_dashboard_service)]
ConfigDependency = Annotated[Config, Depends(get_config)]
MonthQuery = Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")]


class ExpenseCommandRequest(BaseModel):
    text: str = Field(..., examples=["記 餐費 早餐+吉品+便當 590 分215"])


@router.get("/health")
def health(service: DashboardDependency):
    return {
        "status": "ok",
        "source": "demo" if service.sheets.using_demo_data else "google_sheets",
        "lineWebhook": "configured" if service.sheets.config.has_line_config else "missing_config",
    }


@router.post("/webhook")
async def line_webhook(
    request: Request,
    service: DashboardDependency,
    config: ConfigDependency,
    x_line_signature: Annotated[str | None, Header(alias="X-Line-Signature")] = None,
):
    if not config.has_line_config:
        raise HTTPException(status_code=500, detail="LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN 尚未設定")
    if not x_line_signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    try:
        from linebot.v3 import WebhookHandler
        from linebot.v3.exceptions import InvalidSignatureError
        from linebot.v3.messaging import (
            ApiClient,
            Configuration,
            MessagingApi,
            ReplyMessageRequest,
            TextMessage,
        )
        from linebot.v3.webhooks import MessageEvent, TextMessageContent
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="請先安裝 line-bot-sdk") from exc

    body = (await request.body()).decode("utf-8")
    handler = WebhookHandler(config.line_channel_secret)
    line_configuration = Configuration(access_token=config.line_channel_access_token)

    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_text_message(event):
        reply_text = service.handle_line_text(event.message.text)
        with ApiClient(line_configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )

    try:
        handler.handle(body, x_line_signature)
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail="Invalid LINE signature") from exc

    return {"status": "ok"}


@router.get("/api/dashboard")
def dashboard(service: DashboardDependency, month: MonthQuery = None):
    return service.dashboard(month)


@router.get("/api/expense")
def expense(service: DashboardDependency, month: MonthQuery = None):
    return service.expenses(month)


@router.post("/api/expense/command")
def record_expense_command(payload: ExpenseCommandRequest, service: DashboardDependency):
    try:
        return service.record_expense_command(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/summary/monthly")
def monthly_summary(service: DashboardDependency):
    return service.monthly_summary()


@router.get("/api/summary/trend")
def trend(service: DashboardDependency, limit: Annotated[int, Query(ge=1, le=24)] = 6):
    return service.trend(limit=limit)


@router.get("/api/summary/type-breakdown")
def type_breakdown(service: DashboardDependency, month: MonthQuery = None):
    return service.type_breakdown(month)


@router.get("/api/summary/payer-split")
def payer_split(service: DashboardDependency, month: MonthQuery = None):
    return service.payer_split(month)


@router.get("/api/options")
def options(service: DashboardDependency):
    summary = service.monthly_summary()
    return {"months": summary["months"]}
