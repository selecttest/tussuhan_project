from __future__ import annotations

from typing import Any

from config import Config
from demo_data import ALLOCATIONS, EXPENSE_RECORDS, INCOME_RECORDS, SUBSCRIPTIONS


def _to_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return 0
    cleaned = str(value).replace(",", "").replace("NT$", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0


def _normalize_date(value: Any) -> str:
    return str(value or "").replace("-", "/").strip()


def _month_from_date(value: Any) -> str:
    text = _normalize_date(value)
    if len(text) >= 7:
        return text[:7].replace("/", "-")
    return ""


class SheetsClient:
    def __init__(self, config: Config):
        self.config = config
        self._spreadsheet = None

    @property
    def using_demo_data(self) -> bool:
        return self.config.demo_mode or not self.config.has_google_sheets_config

    def income_records(self) -> list[dict[str, Any]]:
        if self.using_demo_data:
            return list(INCOME_RECORDS)

        rows = self._worksheet_records(self.config.income_sheet_name)
        return [
            {
                "name": row.get("名稱", ""),
                "date": _normalize_date(row.get("收入日期")),
                "type": row.get("收入種類", ""),
                "amount": int(_to_number(row.get("收入金額"))),
                "month": row.get("月份總表") or _month_from_date(row.get("收入日期")),
            }
            for row in rows
        ]

    def expense_records(self) -> list[dict[str, Any]]:
        if self.using_demo_data:
            return list(EXPENSE_RECORDS)

        rows = self._worksheet_records(self.config.expense_sheet_name)
        return [
            {
                "date": _normalize_date(row.get("日期")),
                "category": row.get("分類", ""),
                "item": row.get("品項", ""),
                "amount": int(_to_number(row.get("金額"))),
                "month": row.get("月份") or _month_from_date(row.get("日期")),
            }
            for row in rows
        ]

    def allocations(self) -> list[dict[str, Any]]:
        if self.using_demo_data:
            return list(ALLOCATIONS)

        rows = self._worksheet_records(self.config.allocation_sheet_name)
        return [
            {
                "label": row.get("名稱", ""),
                "pct": _to_number(row.get("分配比例")),
                "description": row.get("說明", ""),
            }
            for row in rows
        ]

    def subscriptions(self) -> list[dict[str, Any]]:
        if self.using_demo_data:
            return list(SUBSCRIPTIONS)

        rows = self._worksheet_records(self.config.subscription_sheet_name)
        return [
            {
                "name": row.get("服務名稱", ""),
                "fee": int(_to_number(row.get("每月費用"))),
                "cycle": row.get("計費週期", "月繳"),
                "status": row.get("狀態", "啟用"),
                "icon": row.get("圖示", "pi-credit-card"),
                "color": row.get("顏色", "#64748B"),
            }
            for row in rows
        ]

    def _worksheet_records(self, worksheet_name: str) -> list[dict[str, Any]]:
        worksheet = self._open_spreadsheet().worksheet(worksheet_name)
        return worksheet.get_all_records()

    def _open_spreadsheet(self):
        if self._spreadsheet is not None:
            return self._spreadsheet

        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError as exc:
            raise RuntimeError("請先安裝 gspread 與 google-auth，或設定 DEMO_MODE=true 使用 demo 資料") from exc

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(
            self.config.google_credentials_path,
            scopes=scopes,
        )
        self._spreadsheet = gspread.authorize(credentials).open_by_key(self.config.google_sheets_id)
        return self._spreadsheet
