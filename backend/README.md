# Backend API

Python FastAPI backend for the income planning dashboard. It reads Google Sheets through the Google Sheets API when credentials are configured, and falls back to demo data so the frontend can develop without secrets.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment

```bash
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
CORS_ORIGIN=http://localhost:3000
```

If these values are not set, the API returns demo data.

## Google Sheets

Create a Google Cloud service account, download the JSON key, enable Google Sheets API, and share the spreadsheet with the service account email.

Expected worksheet names and headers:

- `收入紀錄`: `名稱`, `收入日期`, `收入種類`, `收入金額`, `月份總表`
- `支出紀錄`: `日期`, `分類`, `品項`, `金額`, `月份`
- `固定分配設定`: `名稱`, `固定分配金額`, `分配比例`, `說明`
- `訂閱管理`: `服務名稱`, `每月費用`, `計費週期`, `狀態`

Optional environment overrides:

```bash
INCOME_SHEET_NAME=收入紀錄
EXPENSE_SHEET_NAME=支出紀錄
ALLOCATION_SHEET_NAME=固定分配設定
SUBSCRIPTION_SHEET_NAME=訂閱管理
```

## Endpoints

- `GET /health`
- `GET /api/dashboard?month=2026-04`
- `GET /api/income?month=2026-04`
- `GET /api/expense?month=2026-04`
- `GET /api/summary/monthly`
- `GET /api/summary/allocation?month=2026-04`
- `GET /api/summary/trend?limit=6`
- `GET /api/summary/revenue?month=2026-04`
- `GET /api/summary/stats?month=2026-04`
- `GET /api/subscriptions`
- `GET /api/options`

FastAPI docs are available at `http://localhost:8000/docs`.
