from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
import re
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
            "dataSource": "demo" if self.sheets.using_demo_data else "google_sheets",
        }

    def all_expenses(self) -> dict[str, Any]:
        records = self.sheets.expense_records()
        sorted_records = sorted(records, key=lambda r: r.get("date", ""), reverse=True)
        return {
            "total": sum(r["amount"] for r in records),
            "records": sorted_records,
            "availableMonths": sort_months({r["month"] for r in records}),
            "dataSource": "demo" if self.sheets.using_demo_data else "google_sheets",
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

    def update_expense_row(self, sheet_row: int, payload: dict[str, Any]) -> dict[str, Any]:
        if self.sheets.using_demo_data:
            raise ValueError("示範資料模式無法編輯支出，請設定 Google Sheets。")
        amount = int(payload["amount"])
        t_paid = int(payload["tPaid"])
        f_paid = int(payload["fPaid"])
        if t_paid + f_paid != amount:
            raise ValueError("T 付與 F 付合計必須等於總金額")
        payer = str(payload["payer"]).strip().upper()
        if payer not in {"T", "F"}:
            raise ValueError("付款人必須為 T 或 F")
        self.sheets.update_expense_row(
            sheet_row,
            date=str(payload["date"]).strip(),
            expense_type=str(payload["type"]).strip(),
            detail=str(payload["detail"]).strip(),
            amount=amount,
            payer=payer,
            t_paid=t_paid,
            f_paid=f_paid,
        )
        return {"ok": True}

    def delete_expense_row(self, sheet_row: int) -> None:
        if self.sheets.using_demo_data:
            raise ValueError("示範資料模式無法刪除支出，請設定 Google Sheets。")
        self.sheets.delete_expense_row(sheet_row)

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
            if normalized.startswith("查"):
                return self._line_query_summary(normalized)

            if normalized == "今日":
                return self._line_today_summary()

            if normalized == "昨天":
                return self._line_day_summary(date.today() - timedelta(days=1))

            if normalized == "本月":
                return self._line_query_summary("查")

            if normalized.startswith("最近"):
                return self._line_recent_summary(normalized)

            if normalized == "結算":
                return self._line_settlement_summary(current_month())

            if normalized in {"刪", "撤銷"}:
                return self._line_delete_last()

            if normalized in {"help", "Help", "說明", "幫助", "指令"}:
                return self._usage_message()

            multi_commands = self._extract_multi_record_commands(normalized)
            if multi_commands:
                return self._line_record_multiple_success(multi_commands)

            # 新版與舊版記帳格式都交給 parser
            result = self.record_expense_command(normalized)
            return self._line_record_success(result["record"])

        except ValueError as exc:
            return f"{exc}\n\n{self._usage_message()}"

        return self._usage_message()

    def _line_record_success(self, record: dict[str, Any]) -> str:
        month = record.get("month", current_month())
        stats = self.stats(month)
        split = ""
        if record["tPaid"] and record["fPaid"]:
            split = f"\n分擔：T ${record['tPaid']} / F ${record['fPaid']}"
        return (
            "✅ 已記錄\n"
            f"📅 {record['date']}  {record['type']}  {record['detail']}  ${record['amount']} ({record['payer']}付)"
            f"{split}\n\n"
            f"📊 {month}累計\n"
            f"T ${stats['tTotal']}\n"
            f"F ${stats['fTotal']}\n"
            f"合計 ${stats['totalExpense']}"
        )

    def _line_record_multiple_success(self, commands: list[str]) -> str:
        records: list[dict[str, Any]] = []
        for idx, cmd in enumerate(commands, start=1):
            try:
                result = self.record_expense_command(cmd)
            except ValueError as exc:
                raise ValueError(f"第 {idx} 筆格式錯誤：{exc}") from exc
            records.append(result["record"])

        total_added = sum(r["amount"] for r in records)
        preview = "\n".join(
            f"{i}. {r['date']} {r['type']} {r['detail']} ${r['amount']} ({r['payer']}付)"
            for i, r in enumerate(records[:5], start=1)
        )
        if len(records) > 5:
            preview += f"\n...其餘 {len(records) - 5} 筆略"

        by_month: dict[str, dict[str, int]] = {}
        for r in records:
            month = r["month"]
            if month not in by_month:
                s = self.stats(month)
                by_month[month] = {"t": s["tTotal"], "f": s["fTotal"], "total": s["totalExpense"]}

        month_lines = "\n".join(
            f"📊 {m}累計：T ${v['t']} / F ${v['f']} / 合計 ${v['total']}"
            for m, v in sorted(by_month.items())
        )

        return (
            f"✅ 已批次記錄 {len(records)} 筆（合計 ${total_added}）\n"
            f"{preview}\n\n"
            f"{month_lines}"
        )

    def _extract_multi_record_commands(self, text: str) -> list[str]:
        if "\n" not in text and "；" not in text and ";" not in text:
            return []
        chunks: list[str] = []
        for line in text.splitlines():
            for seg in re.split(r"[；;]", line):
                s = seg.strip()
                if s:
                    chunks.append(s)
        return chunks if len(chunks) >= 2 else []

    def _line_query_summary(self, text: str) -> str:
        target = _parse_query_target(text)
        if target["kind"] == "category":
            return self._line_category_summary(target["value"])

        month = target["value"] or current_month()
        stats = self.stats(month)
        settlement = self._line_settlement_summary(month, include_title=False)
        return (
            f"{month} 支出摘要\n"
            f"總支出：${stats['totalExpense']}\n"
            f"T 負擔：${stats['tTotal']}\n"
            f"F 負擔：${stats['fTotal']}\n"
            f"今日：${stats['todayExpense']}\n"
            f"{settlement}"
        )

    def _line_today_summary(self) -> str:
        return self._line_day_summary(date.today())

    def _line_day_summary(self, day: date) -> str:
        day_text = f"{day.year}/{day.month}/{day.day}"
        records = [r for r in self.sheets.expense_records() if r["date"] == day_text]
        total = sum(r["amount"] for r in records)
        if not records:
            return f"尚無支出紀錄。\n日期：{day_text}"

        details = "\n".join(
            f"- {r['type']} {r['detail']}：${r['amount']}"
            for r in records[:5]
        )
        more = f"\n...還有 {len(records) - 5} 筆" if len(records) > 5 else ""
        return f"{day_text} 支出：${total}\n{details}{more}"

    def _line_category_summary(self, category: str) -> str:
        month = current_month()
        records = [r for r in self.sheets.expense_records() if r["month"] == month and r["type"] == category]
        total = sum(r["amount"] for r in records)
        return f"{month} {category} 小計：${total}（{len(records)} 筆）"

    def _line_recent_summary(self, text: str) -> str:
        m = re.fullmatch(r"最近(\d+)?", text)
        if not m:
            raise ValueError("最近指令格式錯誤，請使用：最近 或 最近5")
        limit = int(m.group(1) or 5)
        limit = max(1, min(limit, 20))
        records = sorted(self.sheets.expense_records(), key=lambda r: (r.get("date", ""), r.get("sheetRow", 0)), reverse=True)
        records = records[:limit]
        if not records:
            return "目前沒有任何支出紀錄。"
        lines = [f"- {r['date']} {r['type']} {r['detail']} ${r['amount']} ({r['payer']})" for r in records]
        return f"最近 {len(records)} 筆：\n" + "\n".join(lines)

    def _line_settlement_summary(self, month: str, include_title: bool = True) -> str:
        records = [r for r in self.sheets.expense_records() if r["month"] == month]
        t_total = sum(r["tPaid"] for r in records)
        f_total = sum(r["fPaid"] for r in records)
        delta = t_total - f_total
        title = f"{month} 結算\n" if include_title else ""
        if delta > 0:
            body = f"F 應補 T ${delta // 2}"
        elif delta < 0:
            body = f"T 應補 F ${(-delta) // 2}"
        else:
            body = "本月雙方已結清 ✅"
        return f"{title}T 共付 ${t_total} / F 共付 ${f_total}\n{body}"

    def _line_delete_last(self) -> str:
        if self.sheets.using_demo_data:
            raise ValueError("示範資料模式無法刪除，請先連接 Google Sheets")
        records = [r for r in self.sheets.expense_records() if r.get("sheetRow")]
        if not records:
            return "目前沒有可刪除的紀錄。"
        target = max(records, key=lambda r: int(r["sheetRow"]))
        self.sheets.delete_expense_row(int(target["sheetRow"]))
        return f"✅ 已刪除：{target['date']} {target['type']} {target['detail']} ${target['amount']}"

    def _usage_message(self) -> str:
        return (
            "可用指令清單：\n"
            "📝 記帳\n"
            "• 拉亞 415\n"
            "• F coco 99\n"
            "• 早餐+便當 590 分215\n"
            "• 昨天 拉亞 415\n"
            "• 餐費 拉亞 415\n\n"
            "• 多筆：每筆一行，或用 ; 分隔\n"
            "  例：拉亞 415; F coco 99\n\n"
            "🔍 查詢\n"
            "• 查 / 查 2026-04 / 查 4月 / 查 餐費\n"
            "• 今日 / 昨天 / 本月\n"
            "• 最近 / 最近5\n"
            "• 結算\n\n"
            "✏️ 操作\n"
            "• 刪 / 撤銷\n\n"
            "ℹ️ 說明\n"
            "• help / 說明 / 幫助 / 指令"
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


def _parse_query_target(text: str) -> dict[str, str | None]:
    parts = text.strip().split()
    if len(parts) < 2:
        return {"kind": "month", "value": None}
    value = parts[1].strip()
    try:
        month = _parse_month_query(text)
        if month:
            return {"kind": "month", "value": month}
    except ValueError:
        pass

    category_map = {
        "餐費": "Food",
        "食物": "Food",
        "早餐": "Food",
        "午餐": "Food",
        "晚餐": "Food",
        "飲料": "Drink",
        "喝": "Drink",
        "寶寶": "Baby",
        "嬰兒": "Baby",
        "育兒": "Baby",
        "學費": "Tuition",
        "補習": "Tuition",
        "保險": "Insurance",
        "其他": "Other",
    }
    normalized = category_map.get(value, value.capitalize())
    if normalized in {"Food", "Drink", "Baby", "Tuition", "Insurance", "Other"}:
        return {"kind": "category", "value": normalized}
    raise ValueError("查詢格式錯誤，請使用：查 / 查 2026-04 / 查 4月 / 查 餐費")
