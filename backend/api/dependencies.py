from functools import lru_cache

from config import Config
from services import DashboardService
from sheets_client import SheetsClient


@lru_cache
def get_config() -> Config:
    return Config()


@lru_cache
def get_dashboard_service() -> DashboardService:
    return DashboardService(SheetsClient(get_config()))
