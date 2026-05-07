from config import Config, load_local_env
from services import DashboardService
from sheets_client import SheetsClient


def _config_fingerprint(cfg: Config) -> tuple:
    return (
        cfg.google_sheets_id,
        cfg.google_credentials_path,
        cfg.demo_mode,
        cfg.expense_sheet_name,
    )


_cached_service: DashboardService | None = None
_cached_fingerprint: tuple | None = None


def get_config() -> Config:
    """勿對 Config 做程序級快取：開發時 .env 會更新，需每次重新讀取。"""
    load_local_env()
    return Config()


def get_dashboard_service() -> DashboardService:
    """
    SheetsClient 內含 gspread 連線快取；仅在 GOOGLE_SHEETS_ID／憑證路徑等變更時重建，
    避免每支 API 都重新連線，同時讓 .env 修正後下一個請求即生效。
    """
    global _cached_service, _cached_fingerprint
    load_local_env()
    cfg = Config()
    fp = _config_fingerprint(cfg)
    if _cached_service is not None and _cached_fingerprint == fp:
        return _cached_service
    _cached_service = DashboardService(SheetsClient(cfg))
    _cached_fingerprint = fp
    return _cached_service
