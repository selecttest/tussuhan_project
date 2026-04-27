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
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

If these values are not set, the API returns demo data.

## Google Sheets

Create a Google Cloud service account, download the JSON key, enable Google Sheets API, and share the spreadsheet with the service account email.

Expected worksheet names and headers:

- `收入紀錄`: `名稱`, `收入日期`, `收入種類`, `收入金額`, `月份總表`
- `支出紀錄`: `Date`, `Type`, `Detail`, `Amount`, `Payer`, `T_paid`, `F_paid`
- `固定分配設定`: `名稱`, `固定分配金額`, `分配比例`, `說明`
- `訂閱管理`: `服務名稱`, `每月費用`, `計費週期`, `狀態`

Expense command examples:

- `記 餐費 拉亞+M 415` -> `Payer=T`, `T_paid=415`, `F_paid=0`
- `記F 飲料 coco 99` -> `Payer=F`, `T_paid=0`, `F_paid=99`
- `記 餐費 早餐+吉品+便當 590 分215` -> `Payer=T`, `T_paid=375`, `F_paid=215`
- `收 Z公司 固定收入 15000` -> writes to `收入紀錄`

LINE Bot query examples:

- `查` -> current month summary
- `查 2026-04` or `查 4月` -> selected month summary
- `今日` -> today's expense total
- `本月` -> current month summary
- `訂閱` -> active subscription total

Optional environment overrides:

```bash
INCOME_SHEET_NAME=收入紀錄
EXPENSE_SHEET_NAME=支出紀錄
ALLOCATION_SHEET_NAME=固定分配設定
SUBSCRIPTION_SHEET_NAME=訂閱管理
```

## Endpoints

- `GET /health`
- `POST /webhook`
- `GET /api/dashboard?month=2026-04`
- `GET /api/income?month=2026-04`
- `GET /api/expense?month=2026-04`
- `POST /api/expense/command`
- `GET /api/summary/monthly`
- `GET /api/summary/allocation?month=2026-04`
- `GET /api/summary/trend?limit=6`
- `GET /api/summary/revenue?month=2026-04`
- `GET /api/summary/stats?month=2026-04`
- `GET /api/subscriptions`
- `GET /api/options`

FastAPI docs are available at `http://localhost:8000/docs`.
