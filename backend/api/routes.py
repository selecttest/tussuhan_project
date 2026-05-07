from typing import Annotated
from pathlib import Path as FsPath

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from api.dependencies import get_config, get_dashboard_service
from config import Config
from services import DashboardService


router = APIRouter()
DashboardDependency = Annotated[DashboardService, Depends(get_dashboard_service)]
ConfigDependency = Annotated[Config, Depends(get_config)]
MonthQuery = Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")]


class ExpenseCommandRequest(BaseModel):
    text: str = Field(..., examples=["記 餐費 早餐+吉品+便當 590 分215"])


class ExpenseRowUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    date: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    detail: str = Field(..., min_length=1)
    amount: int = Field(ge=0)
    payer: str = Field(..., min_length=1)
    tPaid: int = Field(ge=0)
    fPaid: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_row(self):
        payer = self.payer.strip().upper()
        if payer not in ("T", "F"):
            raise ValueError("付款人必須為 T 或 F")
        if self.tPaid + self.fPaid != self.amount:
            raise ValueError("T 付 + F 付 必須等於金額")
        return self.model_copy(update={"payer": payer})


@router.get("/health")
def health(service: DashboardDependency, config: ConfigDependency):
    cred = config.google_credentials_path
    cred_ok = bool(cred and FsPath(cred).is_file())
    err = service.sheets.spreadsheet_access_error()
    source = "demo" if service.sheets.using_demo_data else "google_sheets"

    env_file = FsPath(__file__).resolve().parent.parent / ".env"
    env_file_present = env_file.is_file()

    hint = None
    if not config.has_google_sheets_config:
        if env_file_present:
            hint = (
                "偵測到 backend/.env 存在，但 GOOGLE_SHEETS_ID / GOOGLE_CREDENTIALS_PATH 未被載入。"
                "請在終端機按 Ctrl+C 完全關閉 uvicorn 後，在 backend 目錄重新執行："
                "`py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`。"
                "（IDE 除錯執行也需「完全停止」後再啟動，否則設定會卡在快取。）"
            )
        else:
            hint = "請複製 backend/.env.example 為 backend/.env，設定 GOOGLE_SHEETS_ID 與 GOOGLE_CREDENTIALS_PATH 後重啟 uvicorn。"
    elif config.has_google_sheets_config and cred and not cred_ok:
        hint = f"找不到憑證檔案，目前解析路徑為：{cred}"
    elif err and "WorksheetNotFound" in err:
        hint = (
            f"找不到工作表「{config.expense_sheet_name}」。請將試算表底部分頁改名，或設定環境變數 EXPENSE_SHEET_NAME=你的分頁名稱。"
        )

    status = "ok"
    if not service.sheets.using_demo_data and config.has_google_sheets_config:
        if not cred_ok or err:
            status = "degraded"

    return {
        "status": status,
        "source": source,
        "lineWebhook": "configured" if service.sheets.config.has_line_config else "missing_config",
        "demoMode": config.demo_mode,
        "envFilePresent": env_file_present,
        "googleSheets": {
            "sheetIdConfigured": bool(config.google_sheets_id),
            "credentialsPathResolved": cred or None,
            "credentialsFileExists": cred_ok,
            "expenseWorksheet": config.expense_sheet_name,
        },
        "sheetsError": err,
        "hint": hint,
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


@router.get("/api/expense/all")
def expense_all(service: DashboardDependency):
    return service.all_expenses()


@router.get("/api/expense")
def expense(service: DashboardDependency, month: MonthQuery = None):
    return service.expenses(month)


@router.post("/api/expense/command")
def record_expense_command(payload: ExpenseCommandRequest, service: DashboardDependency):
    try:
        return service.record_expense_command(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/api/expense/row/{sheet_row}")
def patch_expense_row(
    sheet_row: Annotated[int, Path(ge=2)],
    payload: ExpenseRowUpdate,
    service: DashboardDependency,
):
    try:
        return service.update_expense_row(sheet_row, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/api/expense/row/{sheet_row}")
def delete_expense_row_endpoint(
    sheet_row: Annotated[int, Path(ge=2)],
    service: DashboardDependency,
):
    try:
        service.delete_expense_row(sheet_row)
        return {"ok": True}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
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
