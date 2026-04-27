from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from expense_parser import parse_expense_command
from income_parser import parse_income_command
from sheets_client import SheetsClient


def current_month() -> str:
    return date.today().strftime("%Y-%m")


def sort_months(months: set[str] | list[str], descending: bool = True) -> list[str]:
    return sorted((month for month in months if month), reverse=descending)


class DashboardService:
    def __init__(self, sheets: SheetsClient):
        self.sheets = sheets

    def income(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.income_records()
        selected_month = month or self._latest_month(records)
        filtered = [record for record in records if record["month"] == selected_month]
        return {
            "month": selected_month,
            "total": sum(record["amount"] for record in filtered),
            "records": filtered,
            "availableMonths": sort_months({record["month"] for record in records}),
        }

    def expenses(self, month: str | None = None) -> dict[str, Any]:
        records = self.sheets.expense_records()
        selected_month = month or self._latest_month(records)
        filtered = [record for record in records if record["month"] == selected_month]
        return {
            "month": selected_month,
            "total": sum(record["amount"] for record in filtered),
            "records": filtered,
            "availableMonths": sort_months({record["month"] for record in records}),
        }

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

    def record_income_command(self, text: str) -> dict[str, Any]:
        command = parse_income_command(text)
        record = self.sheets.append_income(command)
        return {
            "message": "收入記錄成功",
            "record": record,
            "sheetRow": {
                "名稱": command.name,
                "收入日期": command.date,
                "收入種類": command.type,
                "收入金額": command.amount,
                "月份總表": command.month,
            },
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
                    f"{record['type']} - {record['detail']}\n"
                    f"金額：${record['amount']}\n"
                    f"付款：{record['payer']}，T ${record['tPaid']} / F ${record['fPaid']}"
                )

            if normalized.startswith("收 "):
                result = self.record_income_command(normalized)
                record = result["record"]
                return (
                    "收入記錄成功！\n"
                    f"{record['name']} - {record['type']}\n"
                    f"金額：${record['amount']}\n"
                    f"月份：{record['month']}"
                )

            if normalized.startswith("查"):
                return self._line_month_summary(normalized)

            if normalized == "今日":
                return self._line_today_summary()

            if normalized == "本月":
                return self._line_month_summary("查")

            if normalized == "訂閱":
                return self._line_subscriptions_summary()

            if normalized in {"help", "Help", "說明", "幫助"}:
                return self._usage_message()
        except ValueError as exc:
            return f"{exc}\n\n{self._usage_message()}"

        return self._usage_message()

    def revenue(self, month: str | None = None) -> dict[str, Any]:
        income = self.income(month)
        grouped: dict[str, int] = defaultdict(int)
        for record in income["records"]:
            grouped[record["name"]] += record["amount"]

        items = [
            {
                "label": label,
                "value": value,
                "percentage": round((value / income["total"]) * 100, 1) if income["total"] else 0,
            }
            for label, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
        ]

        return {
            "month": income["month"],
            "total": income["total"],
            "items": items,
            "chart": {
                "labels": [item["label"] for item in items],
                "values": [item["value"] for item in items],
            },
        }

    def monthly_summary(self) -> dict[str, Any]:
        income_records = self.sheets.income_records()
        expense_records = self.sheets.expense_records()
        months = sort_months(
            {record["month"] for record in income_records}
            | {record["month"] for record in expense_records},
            descending=True,
        )

        items = []
        for month in months:
            month_income = [record for record in income_records if record["month"] == month]
            month_expense = [record for record in expense_records if record["month"] == month]
            total_income = sum(record["amount"] for record in month_income)
            total_expense = sum(record["amount"] for record in month_expense)
            items.append(
                {
                    "month": month,
                    "totalIncome": total_income,
                    "totalExpense": total_expense,
                    "netIncome": total_income - total_expense,
                    "sources": sorted({record["type"] for record in month_income if record["type"]}),
                }
            )

        return {"items": items, "months": months}

    def trend(self, limit: int = 6) -> dict[str, Any]:
        items = list(reversed(self.monthly_summary()["items"][:limit]))
        return {
            "months": [item["month"] for item in items],
            "incomeValues": [item["totalIncome"] for item in items],
            "expenseValues": [item["totalExpense"] for item in items],
            "items": items,
        }

    def allocation(self, month: str | None = None) -> dict[str, Any]:
        income = self.income(month)
        expenses = self.expenses(income["month"])
        expense_by_category: dict[str, int] = defaultdict(int)
        for record in expenses["records"]:
            expense_by_category[record["category"]] += record["amount"]

        items = []
        for allocation in self.sheets.allocations():
            label = allocation["label"]
            budgeted = round(income["total"] * float(allocation["pct"]) / 100)
            actual = expense_by_category.get(label, 0)
            if label == "生活支出":
                actual += sum(
                    value
                    for category, value in expense_by_category.items()
                    if category in {"餐費", "交通", "日用品", "訂閱", "Food", "Drink", "Baby", "Other"}
                )
            elif label == "教育":
                actual += expense_by_category.get("Tuition", 0)
            items.append(
                {
                    "label": f"{label} {int(float(allocation['pct']))}%",
                    "name": label,
                    "pct": allocation["pct"],
                    "budgeted": budgeted,
                    "actual": actual,
                    "description": allocation.get("description", ""),
                    "status": "over" if actual > budgeted else "ok",
                }
            )

        return {
            "month": income["month"],
            "totalIncome": income["total"],
            "totalExpense": expenses["total"],
            "items": items,
            "chart": {
                "labels": [item["label"] for item in items],
                "budgeted": [item["budgeted"] for item in items],
                "actual": [item["actual"] for item in items],
            },
        }

    def subscriptions(self) -> dict[str, Any]:
        items = [
            item for item in self.sheets.subscriptions()
            if item.get("status") in {"啟用", "active", "Active", ""}
        ]
        total = sum(item["fee"] for item in items)
        return {
            "total": total,
            "count": len(items),
            "items": items,
            "chart": {
                "labels": [item["name"] for item in items],
                "values": [item["fee"] for item in items],
                "colors": [item["color"] for item in items],
            },
        }

    def stats(self, month: str | None = None) -> dict[str, Any]:
        income = self.income(month)
        expenses = self.expenses(income["month"])
        subscriptions = self.subscriptions()
        return {
            "month": income["month"],
            "totalIncome": income["total"],
            "totalExpense": expenses["total"],
            "netIncome": income["total"] - expenses["total"],
            "totalSubscription": subscriptions["total"],
            "subscriptionCount": subscriptions["count"],
        }

    def dashboard(self, month: str | None = None) -> dict[str, Any]:
        selected_month = month or self._latest_month(self.sheets.income_records())
        return {
            "stats": self.stats(selected_month),
            "income": self.income(selected_month),
            "expense": self.expenses(selected_month),
            "revenue": self.revenue(selected_month),
            "allocation": self.allocation(selected_month),
            "trend": self.trend(),
            "subscriptions": self.subscriptions(),
            "monthlySummary": self.monthly_summary(),
        }

    def _latest_month(self, records: list[dict[str, Any]]) -> str:
        months = sort_months({record.get("month", "") for record in records})
        return months[0] if months else current_month()

    def _line_month_summary(self, text: str) -> str:
        month = _parse_month_query(text) or current_month()
        stats = self.stats(month)
        return (
            f"{month} 收支摘要\n"
            f"收入：${stats['totalIncome']}\n"
            f"支出：${stats['totalExpense']}\n"
            f"結餘：${stats['netIncome']}\n"
            f"訂閱：${stats['totalSubscription']} / {stats['subscriptionCount']} 項"
        )

    def _line_today_summary(self) -> str:
        today = date.today()
        today_text = f"{today.year}/{today.month}/{today.day}"
        records = [
            record for record in self.sheets.expense_records()
            if record["date"] == today_text
        ]
        total = sum(record["amount"] for record in records)
        if not records:
            return f"今日尚無支出紀錄。\n日期：{today_text}"

        details = "\n".join(
            f"- {record['type']} {record['detail']}：${record['amount']}"
            for record in records[:5]
        )
        more = f"\n...還有 {len(records) - 5} 筆" if len(records) > 5 else ""
        return f"今日支出：${total}\n{details}{more}"

    def _line_subscriptions_summary(self) -> str:
        subscriptions = self.subscriptions()
        if not subscriptions["items"]:
            return "目前沒有啟用中的訂閱。"

        details = "\n".join(
            f"- {item['name']}：${item['fee']}"
            for item in subscriptions["items"][:8]
        )
        more = f"\n...還有 {len(subscriptions['items']) - 8} 項" if len(subscriptions["items"]) > 8 else ""
        return f"每月訂閱合計：${subscriptions['total']}\n{details}{more}"

    def _usage_message(self) -> str:
        return (
            "可用指令：\n"
            "記 餐費 拉亞+M 415\n"
            "記F 飲料 coco 99\n"
            "記 餐費 早餐+便當 590 分215\n"
            "收 Z公司 固定收入 15000\n"
            "查 或 查 2026-04\n"
            "今日 / 本月 / 訂閱"
        )


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
