from __future__ import annotations

from typing import Any

from config import Config
from demo_data import EXPENSE_RECORDS
from expense_parser import ExpenseCommand


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
    parts = text.split("/")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}"
    return ""


class SheetsClient:
    def __init__(self, config: Config):
        self.config = config
        self._spreadsheet = None

    @property
    def using_demo_data(self) -> bool:
        return self.config.demo_mode or not self.config.has_google_sheets_config

    def expense_records(self) -> list[dict[str, Any]]:
        if self.using_demo_data:
            return list(EXPENSE_RECORDS)

        rows = self._worksheet_records(self.config.expense_sheet_name)
        return [self._normalize_expense_row(row) for row in rows]

    def append_expense(self, command: ExpenseCommand) -> dict[str, Any]:
        if self.using_demo_data:
            return command.to_record()

        worksheet = self._open_spreadsheet().worksheet(self.config.expense_sheet_name)
        worksheet.append_row(command.to_sheet_row(), value_input_option="USER_ENTERED")
        return command.to_record()

    def _worksheet_records(self, worksheet_name: str) -> list[dict[str, Any]]:
        worksheet = self._open_spreadsheet().worksheet(worksheet_name)
        return worksheet.get_all_records()

    def _normalize_expense_row(self, row: dict[str, Any]) -> dict[str, Any]:
        expense_date = _normalize_date(row.get("Date") or row.get("日期"))
        expense_type = row.get("Type") or row.get("分類") or ""
        detail = row.get("Detail") or row.get("品項") or ""
        amount = int(_to_number(row.get("Amount") or row.get("金額")))
        payer = str(row.get("Payer") or "T").upper()
        t_paid = int(_to_number(row.get("T_paid")))
        f_paid = int(_to_number(row.get("F_paid")))

        if not t_paid and not f_paid:
            t_paid, f_paid = (amount, 0) if payer == "T" else (0, amount)

        return {
            "date": expense_date,
            "category": expense_type,
            "type": expense_type,
            "item": detail,
            "detail": detail,
            "amount": amount,
            "payer": payer,
            "tPaid": t_paid,
            "fPaid": f_paid,
            "t_paid": t_paid,
            "f_paid": f_paid,
            "month": _month_from_date(expense_date),
        }

    def _open_spreadsheet(self):
        if self._spreadsheet is not None:
            return self._spreadsheet

        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError as exc:
            raise RuntimeError("請先安裝 gspread 與 google-auth") from exc

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(
            self.config.google_credentials_path,
            scopes=scopes,
        )
        self._spreadsheet = gspread.authorize(credentials).open_by_key(self.config.google_sheets_id)
        return self._spreadsheet
