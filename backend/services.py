from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from expense_parser import parse_expense_command
from sheets_client import SheetsClient


def current_month() -> str:
    return date.today().strftime("%Y-%m")


def sort_months(months: set[str] | list[str], descending: bool = True) -> list[str]:
    return sorted((m for m in months if m), reverse=descending)


class DashboardService:
    def __init__(self, sheets: SheetsClient):
        self.sheets = sheets

    def expenses(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        filtered = [r for r in records if r["month"] == selected_month]
        return {
            "month": selected_month,
            "total": sum(r["amount"] for r in filtered),
            "records": filtered,
            "availableMonths": sort_months({r["month"] for r in records}),
        }

    def all_expenses(self) -> dict[str, Any]:
        records = self.sheets.expense_records()
        sorted_records = sorted(records, key=lambda r: r.get("date", ""), reverse=True)
        return {
            "total": sum(r["amount"] for r in records),
            "records": sorted_records,
            "availableMonths": sort_months({r["month"] for r in records}),
        }

    def stats(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        filtered = [r for r in records if r["month"] == selected_month]
        total = sum(r["amount"] for r in filtered)
        t_total = sum(r["tPaid"] for r in filtered)
        f_total = sum(r["fPaid"] for r in filtered)

        today = date.today()
        today_text = f"{today.year}/{today.month}/{today.day}"
        today_records = [r for r in records if r["date"] == today_text]
        today_total = sum(r["amount"] for r in today_records)

        return {
            "month": selected_month,
            "totalExpense": total,
            "tTotal": t_total,
            "fTotal": f_total,
            "todayExpense": today_total,
        }

    def type_breakdown(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        filtered = [r for r in records if r["month"] == selected_month]

        grouped: dict[str, int] = defaultdict(int)
        for r in filtered:
            grouped[r["type"]] += r["amount"]

        total = sum(grouped.values())
        items = [
            {
                "label": label,
                "value": value,
                "percentage": round((value / total) * 100, 1) if total else 0,
            }
            for label, value in sorted(grouped.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "month": selected_month,
            "total": total,
            "items": items,
            "chart": {
                "labels": [item["label"] for item in items],
                "values": [item["value"] for item in items],
            },
        }

    def payer_split(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        filtered = [r for r in records if r["month"] == selected_month]

        t_total = sum(r["tPaid"] for r in filtered)
        f_total = sum(r["fPaid"] for r in filtered)

        by_type: dict[str, dict[str, int]] = defaultdict(lambda: {"tPaid": 0, "fPaid": 0})
        for r in filtered:
            by_type[r["type"]]["tPaid"] += r["tPaid"]
            by_type[r["type"]]["fPaid"] += r["fPaid"]

        by_type_list = sorted(
            [{"type": t, "tPaid": v["tPaid"], "fPaid": v["fPaid"]} for t, v in by_type.items()],
            key=lambda x: x["tPaid"] + x["fPaid"],
            reverse=True,
        )

        return {
            "month": selected_month,
            "tTotal": t_total,
            "fTotal": f_total,
            "byType": by_type_list,
            "chart": {
                "labels": ["T 負擔", "F 負擔"],
                "values": [t_total, f_total],
            },
        }

    def trend(self, limit: int = 6) -> dict[str, Any]:
        records = self.sheets.expense_records()
        months = sort_months({r.get("month", "") for r in records})[:limit]
        months = list(reversed(months))

        items = []
        for month in months:
            filtered = [r for r in records if r["month"] == month]
            total = sum(r["amount"] for r in filtered)
            t_total = sum(r["tPaid"] for r in filtered)
            f_total = sum(r["fPaid"] for r in filtered)
            items.append({"month": month, "totalExpense": total, "tTotal": t_total, "fTotal": f_total})

        return {
            "months": [item["month"] for item in items],
            "expenseValues": [item["totalExpense"] for item in items],
            "tValues": [item["tTotal"] for item in items],
            "fValues": [item["fTotal"] for item in items],
            "items": items,
        }

    def monthly_summary(self) -> dict[str, Any]:
        records = self.sheets.expense_records()
        months = sort_months({r.get("month", "") for r in records})

        items = []
        for month in months:
            filtered = [r for r in records if r["month"] == month]
            total = sum(r["amount"] for r in filtered)
            t_total = sum(r.get("tPaid", 0) for r in filtered)
            f_total = sum(r.get("fPaid", 0) for r in filtered)
            items.append({
                "month": month,
                "totalExpense": total,
                "tTotal": t_total,
                "fTotal": f_total,
                "count": len(filtered),
            })

        return {"items": items, "months": months}

    def record_expense_command(self, text: str) -> dict[str, Any]:
        command = parse_expense_command(text)
        record = self.sheets.append_expense(command)
        return {
            "message": "記帳成功",
            "record": record,
            "sheetRow": {
                "Date": command.date,
                "Type": command.type,
                "Detail": command.detail,
                "Amount": command.amount,
                "Payer": command.payer,
                "T_paid": command.t_paid,
                "F_paid": command.f_paid,
            },
        }

    def dashboard(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        return {
            "stats": self.stats(selected_month),
            "typeBreakdown": self.type_breakdown(selected_month),
            "trend": self.trend(),
            "payerSplit": self.payer_split(selected_month),
            "expense": self.expenses(selected_month),
            "monthlySummary": self.monthly_summary(),
        }

    def handle_line_text(self, text: str) -> str:
        normalized = text.strip()
        if not normalized:
            return self._usage_message()

        try:
            if normalized.startswith("記"):
                result = self.record_expense_command(normalized)
                record = result["record"]
                return (
                    "記帳成功！\n"
                    f"{record['type']} — {record['detail']}\n"
                    f"金額：${record['amount']}\n"
                    f"付款：{record['payer']}，T ${record['tPaid']} / F ${record['fPaid']}"
                )

            if normalized.startswith("查"):
                return self._line_month_summary(normalized)

            if normalized == "今日":
                return self._line_today_summary()

            if normalized == "本月":
                return self._line_month_summary("查")

            if normalized in {"help", "Help", "說明", "幫助"}:
                return self._usage_message()

        except ValueError as exc:
            return f"{exc}\n\n{self._usage_message()}"

        return self._usage_message()

    def _line_month_summary(self, text: str) -> str:
        month = _parse_month_query(text) or current_month()
        stats = self.stats(month)
        return (
            f"{month} 支出摘要\n"
            f"總支出：${stats['totalExpense']}\n"
            f"T 負擔：${stats['tTotal']}\n"
            f"F 負擔：${stats['fTotal']}\n"
            f"今日：${stats['todayExpense']}"
        )

    def _line_today_summary(self) -> str:
        today = date.today()
        today_text = f"{today.year}/{today.month}/{today.day}"
        records = [r for r in self.sheets.expense_records() if r["date"] == today_text]
        total = sum(r["amount"] for r in records)
        if not records:
            return f"今日尚無支出紀錄。\n日期：{today_text}"

        details = "\n".join(
            f"- {r['type']} {r['detail']}：${r['amount']}"
            for r in records[:5]
        )
        more = f"\n...還有 {len(records) - 5} 筆" if len(records) > 5 else ""
        return f"今日支出：${total}\n{details}{more}"

    def _usage_message(self) -> str:
        return (
            "可用指令：\n"
            "記 餐費 拉亞+M 415\n"
            "記F 飲料 coco 99\n"
            "記 餐費 早餐+便當 590 分215\n"
            "查 或 查 2026-04\n"
            "今日 / 本月"
        )

    def _latest_month(self, records: list[dict[str, Any]]) -> str:
        months = sort_months({r.get("month", "") for r in records})
        return months[0] if months else current_month()


def _parse_month_query(text: str) -> str | None:
    parts = text.strip().split()
    if len(parts) < 2:
        return None

    value = parts[1].strip()
    if len(value) == 7 and value[4] == "-" and value[:4].isdigit() and value[5:].isdigit():
        return value

    if value.endswith("月") and value[:-1].isdigit():
        month = int(value[:-1])
        if 1 <= month <= 12:
            return f"{date.today().year:04d}-{month:02d}"

    raise ValueError("查詢月份格式錯誤，請使用：查 2026-04 或 查 4月")
