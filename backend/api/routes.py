from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_dashboard_service
from services import DashboardService


router = APIRouter()
DashboardDependency = Annotated[DashboardService, Depends(get_dashboard_service)]
MonthQuery = Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")]


@router.get("/health")
def health(service: DashboardDependency):
    return {
        "status": "ok",
        "source": "demo" if service.sheets.using_demo_data else "google_sheets",
    }


@router.get("/api/dashboard")
def dashboard(service: DashboardDependency, month: MonthQuery = None):
    return service.dashboard(month)


@router.get("/api/income")
def income(service: DashboardDependency, month: MonthQuery = None):
    return service.income(month)


@router.get("/api/expense")
def expense(service: DashboardDependency, month: MonthQuery = None):
    return service.expenses(month)


@router.get("/api/summary/monthly")
def monthly_summary(service: DashboardDependency):
    return service.monthly_summary()


@router.get("/api/summary/allocation")
def allocation(service: DashboardDependency, month: MonthQuery = None):
    return service.allocation(month)


@router.get("/api/summary/trend")
def trend(service: DashboardDependency, limit: Annotated[int, Query(ge=1, le=24)] = 6):
    return service.trend(limit=limit)


@router.get("/api/summary/revenue")
def revenue(service: DashboardDependency, month: MonthQuery = None):
    return service.revenue(month)


@router.get("/api/summary/stats")
def stats(service: DashboardDependency, month: MonthQuery = None):
    return service.stats(month)


@router.get("/api/subscriptions")
def subscriptions(service: DashboardDependency):
    return service.subscriptions()


@router.get("/api/options")
def options(service: DashboardDependency):
    monthly = service.monthly_summary()
    return {"months": monthly["months"]}
