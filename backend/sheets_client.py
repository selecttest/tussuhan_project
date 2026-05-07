from __future__ import annotations

from typing import Any

from config import Config
from demo_data import EXPENSE_RECORDS
from expense_parser import ExpenseCommand

# 寫回試算表時依表頭別名找欄位（列順序與使用者 Sheet 一致）
_EXPENSE_HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("Date", "日期"),
    "type": ("Type", "分類"),
    "detail": ("Detail", "品項"),
    "amount": ("Amount", "金額"),
    "payer": ("Payer", "付款"),
    "t_paid": ("T_paid", "T paid", "T付"),
    "f_paid": ("F_paid", "F paid", "F付"),
}


def _resolve_header_index(headers: list[str], aliases: tuple[str, ...]) -> int | None:
    stripped = [h.strip() for h in headers]
    for a in aliases:
        if a in stripped:
            return stripped.index(a)
    return None


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


def _is_year(s: str) -> bool:
    return s.isdigit() and 1990 <= int(s) <= 2100


def _is_month(s: str) -> bool:
    return s.isdigit() and 1 <= int(s) <= 12


def _month_from_date(value: Any) -> str:
    # Handle Python date/datetime objects directly
    if hasattr(value, "year") and hasattr(value, "month"):
        if 1990 <= value.year <= 2100 and 1 <= value.month <= 12:
            return f"{value.year:04d}-{value.month:02d}"
        return ""

    text = _normalize_date(value).split()[0].split("T")[0]
    parts = text.split("/")

    if len(parts) < 2:
        return ""

    # YYYY/M/D or YYYY/MM/DD (app standard)
    if _is_year(parts[0]) and _is_month(parts[1]):
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}"

    # M/D/YYYY or MM/DD/YYYY (US format — gspread may return this)
    if len(parts) >= 3 and _is_year(parts[2]) and _is_month(parts[0]):
        return f"{int(parts[2]):04d}-{int(parts[0]):02d}"

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
            return [dict(r) for r in EXPENSE_RECORDS]

        worksheet = self._open_spreadsheet().worksheet(self.config.expense_sheet_name)
        all_values = worksheet.get_all_values()
        if not all_values:
            return []

        results: list[dict[str, Any]] = []
        for row_num, row_vals in enumerate(all_values[1:], start=2):
            if not row_vals or not any(str(c).strip() for c in row_vals):
                continue
            row_dict: dict[str, Any] = {}
            for i, h in enumerate(all_values[0]):
                key = h.strip()
                row_dict[key] = row_vals[i] if i < len(row_vals) else ""
            normalized = self._normalize_expense_row(row_dict)
            if normalized["month"] and normalized["amount"] > 0:
                normalized["sheetRow"] = row_num
                results.append(normalized)
        return results

    def append_expense(self, command: ExpenseCommand) -> dict[str, Any]:
        if self.using_demo_data:
            return command.to_record()

        worksheet = self._open_spreadsheet().worksheet(self.config.expense_sheet_name)
        worksheet.append_row(command.to_sheet_row(), value_input_option="USER_ENTERED")
        return command.to_record()

    def update_expense_row(
        self,
        sheet_row: int,
        *,
        date: str,
        expense_type: str,
        detail: str,
        amount: int,
        payer: str,
        t_paid: int,
        f_paid: int,
    ) -> None:
        if self.using_demo_data:
            raise RuntimeError("示範資料模式無法編輯支出")

        if sheet_row < 2:
            raise ValueError("列號無效")

        payer = payer.strip().upper()
        if payer not in {"T", "F"}:
            raise ValueError("付款人必須為 T 或 F")

        worksheet = self._open_spreadsheet().worksheet(self.config.expense_sheet_name)
        all_values = worksheet.get_all_values()
        if not all_values or sheet_row > len(all_values):
            raise ValueError("找不到該列")

        headers_raw = all_values[0]
        headers = [h.strip() for h in headers_raw]
        row_vals = list(all_values[sheet_row - 1])
        while len(row_vals) < len(headers):
            row_vals.append("")

        def _write(field: str, value: str) -> None:
            aliases = _EXPENSE_HEADER_ALIASES[field]
            idx = _resolve_header_index(headers_raw, aliases)
            if idx is None:
                raise ValueError(f"試算表缺少欄位：{aliases[0]}")
            row_vals[idx] = value

        _write("date", _normalize_date(date))
        _write("type", expense_type.strip())
        _write("detail", detail.strip())
        _write("amount", str(int(amount)))
        _write("payer", payer)
        _write("t_paid", str(int(t_paid)))
        _write("f_paid", str(int(f_paid)))

        try:
            from gspread.utils import rowcol_to_a1
        except ImportError as exc:
            raise RuntimeError("請先安裝 gspread") from exc

        end_a1 = rowcol_to_a1(sheet_row, len(headers))
        rng = f"A{sheet_row}:{end_a1}"
        worksheet.update(rng, [row_vals[: len(headers)]], value_input_option="USER_ENTERED")

    def delete_expense_row(self, sheet_row: int) -> None:
        if self.using_demo_data:
            raise RuntimeError("示範資料模式無法刪除支出")

        if sheet_row < 2:
            raise ValueError("列號無效")

        worksheet = self._open_spreadsheet().worksheet(self.config.expense_sheet_name)
        all_values = worksheet.get_all_values()
        if not all_values or sheet_row > len(all_values):
            raise ValueError("找不到該列")

        worksheet.delete_rows(sheet_row)

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

    def spreadsheet_access_error(self) -> str | None:
        """若已設定要連試算表，嘗試開啟並找支出工作表；失敗則回傳錯誤說明。"""
        if self.using_demo_data:
            return None
        try:
            sh = self._open_spreadsheet()
            sh.worksheet(self.config.expense_sheet_name)
            return None
        except Exception as exc:  # noqa: BLE001
            return str(exc)
