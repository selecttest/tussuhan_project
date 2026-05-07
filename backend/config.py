import os
import re
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv() -> None:
    """載入 backend/.env。即使未安裝 python-dotenv 也會用內建解析寫入 os.environ。"""
    backend_dir = Path(__file__).resolve().parent
    env_path = backend_dir / ".env"
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
    except ImportError:
        pass
    _apply_env_file(env_path, override=False)


def _apply_env_file(path: Path, *, override: bool = False) -> None:
    """不依賴第三方套件讀取 .env。override=False 時不覆寫已在環境裡的非空變數。"""
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip().lstrip("\ufeff")
        if not key or key.startswith("#"):
            continue
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        # override=True：以 .env 檔為準（開發時每次 load_local_env 套用）
        # override=False：啟動時不覆寫痾統／容器已注入的變數
        if override:
            os.environ[key] = val
            continue
        prev = os.environ.get(key)
        if prev is None or prev == "":
            os.environ[key] = val


def load_local_env() -> None:
    """每次建立 Config 前呼叫：開發時更新 .env 後不必重啟 uvicorn（backend/.env 優先）。"""
    p = Path(__file__).resolve().parent / ".env"
    if p.is_file():
        _apply_env_file(p, override=True)


_load_dotenv()


def _env_str(key: str, default: str = "") -> str:
    v = os.getenv(key, default) or ""
    v = v.strip().strip('"').strip("'")
    if v.startswith("\ufeff"):
        v = v.lstrip("\ufeff")
    return v


def _env_bool(key: str) -> bool:
    return os.getenv(key, "").lower() in {"1", "true", "yes"}


def _normalize_google_sheets_id(raw: str) -> str:
    """支援貼上完整試算表網址，或含雜字元時只保留 ID。"""
    if not raw:
        return ""
    raw = raw.strip()
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", raw)
    if m:
        return m.group(1)
    return raw.split("/")[0].split("?")[0].strip()


def _resolve_credentials_path(raw: str) -> str:
    """轉成絕對路徑；相對路徑則依 backend 目錄解析。"""
    if not raw:
        return ""
    p = Path(raw.replace("\\", os.sep))
    p = p.expanduser()
    if not p.is_absolute():
        p = (Path(__file__).resolve().parent / p).resolve()
    return str(p)


@dataclass(frozen=True)
class Config:
    google_sheets_id: str = field(
        default_factory=lambda: _normalize_google_sheets_id(_env_str("GOOGLE_SHEETS_ID"))
    )
    google_credentials_path: str = field(
        default_factory=lambda: _resolve_credentials_path(_env_str("GOOGLE_CREDENTIALS_PATH"))
    )
    cors_origin: str = field(
        default_factory=lambda: _env_str("CORS_ORIGIN", "*") or "*"
    )
    demo_mode: bool = field(default_factory=lambda: _env_bool("DEMO_MODE"))
    line_channel_secret: str = field(default_factory=lambda: _env_str("LINE_CHANNEL_SECRET"))
    line_channel_access_token: str = field(
        default_factory=lambda: _env_str("LINE_CHANNEL_ACCESS_TOKEN")
    )
    expense_sheet_name: str = field(
        default_factory=lambda: _env_str("EXPENSE_SHEET_NAME", "支出紀錄") or "支出紀錄"
    )

    @property
    def has_google_sheets_config(self) -> bool:
        return bool(self.google_sheets_id and self.google_credentials_path)

    @property
    def has_line_config(self) -> bool:
        return bool(self.line_channel_secret and self.line_channel_access_token)
