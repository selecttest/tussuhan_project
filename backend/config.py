import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    google_sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")
    google_credentials_path: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
    cors_origin: str = os.getenv("CORS_ORIGIN", "*")
    demo_mode: bool = os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}
    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    expense_sheet_name: str = os.getenv("EXPENSE_SHEET_NAME", "支出紀錄")

    @property
    def has_google_sheets_config(self) -> bool:
        return bool(self.google_sheets_id and self.google_credentials_path)

    @property
    def has_line_config(self) -> bool:
        return bool(self.line_channel_secret and self.line_channel_access_token)
