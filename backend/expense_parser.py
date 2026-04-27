from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re


CATEGORY_ALIASES = {
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
    "其他": "Other",
}


@dataclass(frozen=True)
class ExpenseCommand:
    date: str
    type: str
    detail: str
    amount: int
    payer: str
    t_paid: int
    f_paid: int

    @property
    def month(self) -> str:
        year, month, *_ = self.date.split("/")
        return f"{int(year):04d}-{int(month):02d}"

    def to_record(self) -> dict:
        return {
            "date": self.date,
            "category": self.type,
            "type": self.type,
            "item": self.detail,
            "detail": self.detail,
            "amount": self.amount,
            "payer": self.payer,
            "tPaid": self.t_paid,
            "fPaid": self.f_paid,
            "t_paid": self.t_paid,
            "f_paid": self.f_paid,
            "month": self.month,
        }

    def to_sheet_row(self) -> list:
        return [
            self.date,
            self.type,
            self.detail,
            self.amount,
            self.payer,
            self.t_paid,
            self.f_paid,
        ]


def parse_expense_command(text: str, today: date | None = None) -> ExpenseCommand:
    parts = text.strip().split()
    if len(parts) < 4:
        raise ValueError("格式錯誤，請使用：記 餐費 拉亞+M 415 或 記F 飲料 coco 99")

    command = parts[0]
    payer = _parse_payer(command)
    expense_type = CATEGORY_ALIASES.get(parts[1], parts[1])
    detail = parts[2]
    amount = _parse_amount(parts[3], "金額")
    split_amount = _parse_split_amount(parts[4:])
    t_paid, f_paid = _split_paid_amount(amount, payer, split_amount)
    record_date = today or date.today()

    return ExpenseCommand(
        date=f"{record_date.year}/{record_date.month}/{record_date.day}",
        type=expense_type,
        detail=detail,
        amount=amount,
        payer=payer,
        t_paid=t_paid,
        f_paid=f_paid,
    )


def _parse_payer(command: str) -> str:
    match = re.fullmatch(r"記([TFtf]?)", command)
    if not match:
        raise ValueError("指令需以「記」或「記F」開頭")
    return (match.group(1) or "T").upper()


def _parse_amount(value: str, field_name: str) -> int:
    if not re.fullmatch(r"\d+", value):
        raise ValueError(f"{field_name}必須是整數")
    return int(value)


def _parse_split_amount(parts: list[str]) -> int:
    if not parts:
        return 0
    if len(parts) == 1 and parts[0].startswith("分"):
        return _parse_amount(parts[0][1:], "分帳金額")
    if len(parts) == 2 and parts[0] == "分":
        return _parse_amount(parts[1], "分帳金額")
    raise ValueError("分帳格式錯誤，請使用：分215 或 分 215")


def _split_paid_amount(amount: int, payer: str, split_amount: int) -> tuple[int, int]:
    if split_amount < 0 or split_amount > amount:
        raise ValueError("分帳金額不可小於 0 或大於總金額")
    if split_amount == 0:
        return (amount, 0) if payer == "T" else (0, amount)
    if payer == "T":
        return amount - split_amount, split_amount
    return split_amount, amount - split_amount
