from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re


@dataclass(frozen=True)
class IncomeCommand:
    name: str
    date: str
    type: str
    amount: int
    month: str

    def to_record(self) -> dict:
        return {
            "name": self.name,
            "date": self.date,
            "type": self.type,
            "amount": self.amount,
            "month": self.month,
        }

    def to_sheet_row(self) -> list:
        return [
            self.name,
            self.date,
            self.type,
            self.amount,
            self.month,
        ]


def parse_income_command(text: str, today: date | None = None) -> IncomeCommand:
    parts = text.strip().split()
    if len(parts) < 4:
        raise ValueError("格式錯誤，請使用：收 Z公司 固定收入 15000")

    if parts[0] != "收":
        raise ValueError("指令需以「收」開頭")

    amount = _parse_amount(parts[-1])
    income_type = parts[-2]
    name = " ".join(parts[1:-2]).strip()
    if not name:
        raise ValueError("收入名稱不可空白")

    record_date = today or date.today()
    month = f"{record_date.year:04d}-{record_date.month:02d}"

    return IncomeCommand(
        name=name,
        date=f"{record_date.year}/{record_date.month}/{record_date.day}",
        type=income_type,
        amount=amount,
        month=month,
    )


def _parse_amount(value: str) -> int:
    if not re.fullmatch(r"\d+", value):
        raise ValueError("收入金額必須是整數")
    return int(value)
