from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
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
    "保險": "Insurance",
    "保費": "Insurance",
    "其他": "Other",
}

CANONICAL_CATEGORIES = {"Food", "Drink", "Baby", "Tuition", "Insurance", "Other"}
DATE_M_D_RE = re.compile(r"^(\d{1,2})/(\d{1,2})$")
DATE_Y_M_D_RE = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})$")

DETAIL_CATEGORY_HINTS = {
    "Food": ("拉亞", "便當", "火鍋", "麵", "鴨肉", "早餐", "午餐", "晚餐", "咖啡", "聚餐"),
    "Drink": ("coco", "可不可", "手搖", "飲料", "茶", "天仁", "迷客夏"),
    "Baby": ("尿布", "奶粉", "米餅", "副食品", "健保", "嬰兒", "育兒"),
    "Tuition": ("學費", "補習", "課程", "教材"),
    "Insurance": ("保險", "保費"),
    "Other": (),
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
    inferred_other_no_keyword: bool = False

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
            "inferredOtherNoKeyword": self.inferred_other_no_keyword,
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
    if len(parts) < 2:
        raise ValueError("格式錯誤，請使用：拉亞 415 / F coco 99 / 昨天 拉亞 415")

    base_date = today or date.today()
    record_date, idx = _parse_record_date(parts, base_date)

    payer: str | None = None
    expense_type: str | None = None

    # 相容舊版：記/記F [分類] [品項] [金額] [分X]
    if idx < len(parts) and re.fullmatch(r"記([TFtf]?)", parts[idx]):
        payer = _parse_legacy_payer(parts[idx])
        idx += 1
        if idx >= len(parts):
            raise ValueError("缺少分類，請使用：記 餐費 拉亞+M 415")
        expense_type = _normalize_category(parts[idx])
        idx += 1

    # 新版可選類別
    if expense_type is None and idx < len(parts):
        maybe_type = _normalize_category(parts[idx], strict=False)
        if maybe_type is not None:
            expense_type = maybe_type
            idx += 1

    # 新版可選付款人（F/T）
    if payer is None and idx < len(parts) and parts[idx].upper() in {"F", "T"}:
        payer = parts[idx].upper()
        idx += 1

    if idx + 1 >= len(parts):
        raise ValueError("格式錯誤，請使用：拉亞 415 / F coco 99 / 早餐+便當 590 分215")

    detail = parts[idx]
    amount = _parse_amount(parts[idx + 1], "金額")
    split_amount = _parse_split_amount(parts[idx + 2 :])

    payer = payer or "T"
    used_category_inference = expense_type is None
    if used_category_inference:
        expense_type = _infer_category_from_detail(detail)
    inferred_other_no_keyword = used_category_inference and expense_type == "Other"
    t_paid, f_paid = _split_paid_amount(amount, payer, split_amount)

    return ExpenseCommand(
        date=f"{record_date.year}/{record_date.month}/{record_date.day}",
        type=expense_type,
        detail=detail,
        amount=amount,
        payer=payer,
        t_paid=t_paid,
        f_paid=f_paid,
        inferred_other_no_keyword=inferred_other_no_keyword,
    )


def _parse_record_date(parts: list[str], today: date) -> tuple[date, int]:
    token = parts[0]
    if token == "昨天":
        d = today - timedelta(days=1)
        return d, 1
    if token == "前天":
        d = today - timedelta(days=2)
        return d, 1
    if m := DATE_M_D_RE.fullmatch(token):
        month = int(m.group(1))
        day = int(m.group(2))
        d = date(today.year, month, day)
        _validate_record_date(d, today)
        return d, 1
    if m := DATE_Y_M_D_RE.fullmatch(token):
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        _validate_record_date(d, today)
        return d, 1
    return today, 0


def _validate_record_date(record_date: date, today: date) -> None:
    if record_date > today:
        raise ValueError("補記日期不可為未來日期")
    if (today - record_date).days > 30:
        raise ValueError("補記日期不可早於 30 天前")


def _parse_legacy_payer(command: str) -> str:
    match = re.fullmatch(r"記([TFtf]?)", command)
    if not match:
        raise ValueError("舊版指令需以「記」或「記F」開頭")
    return (match.group(1) or "T").upper()


def _normalize_category(token: str, strict: bool = True) -> str | None:
    if token in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[token]
    normalized = token.strip().capitalize()
    if normalized in CANONICAL_CATEGORIES:
        return normalized
    if strict:
        raise ValueError(f"不支援的分類：{token}")
    return None


def _infer_category_from_detail(detail: str) -> str:
    text = detail.lower()
    for category, hints in DETAIL_CATEGORY_HINTS.items():
        if any(h.lower() in text for h in hints):
            return category
    return "Other"


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
