from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

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
                    if category in {"餐費", "交通", "日用品", "訂閱"}
                )
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
