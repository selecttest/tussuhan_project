# 💰 收入理財規劃 Dashboard — LINE Bot 記帳系統

> 自由工作者專屬的收支管理系統，透過 LINE Bot 快速記帳，搭配 Web Dashboard 視覺化財務狀況，資料儲存於 Google Sheets。

---

## 📋 目錄

- [專案概覽](#專案概覽)
- [系統架構](#系統架構)
- [Dashboard 功能模組](#dashboard-功能模組)
- [技術棧](#技術棧)
- [運作流程](#運作流程)
- [資料結構設計](#資料結構設計)
- [部署環境](#部署環境)
- [安裝與設定](#安裝與設定)
- [LINE Bot 指令格式](#line-bot-指令格式)
- [開發規劃](#開發規劃)

---

## 專案概覽

本專案是一套完整的個人財務管理系統，由三個核心元件組成：

1. **LINE Bot（輸入端）**：透過 LINE Messaging API 接收使用者的記帳訊息，支援自然語言輸入收入與支出。
2. **Backend API（處理端）**：Python Flask/FastAPI 應用，部署於 GCP e2-micro 免費 VM，負責解析訊息、操作 Google Sheets、提供 Dashboard API。
3. **Web Dashboard（展示端）**：前端 SPA 應用，以圖表和表格呈現收支紀錄、營收分析、預算分配等財務資訊。

---

## 系統架構

```
┌─────────────┐    Webhook POST     ┌──────────────────────────────────────────┐
│  LINE App   │ ──────────────────▶  │         GCP e2-micro VM (免費方案)        │
│  (使用者)    │ ◀────────────────── │                                          │
└─────────────┘    Reply Message    │  ┌──────────┐    ┌───────────────────┐   │
                                     │  │  Nginx   │───▶│  Python App       │   │
┌─────────────┐    HTTPS (API)      │  │ (SSL/反向 │    │  Flask / FastAPI  │   │
│  Dashboard  │ ◀──────────────────▶│  │  Proxy)  │◀───│                   │   │
│  (瀏覽器)    │                     │  └──────────┘    │  - LINE Webhook   │   │
└─────────────┘                     │                   │  - REST API       │   │
                                     │                   │  - 訊息解析引擎    │   │
                                     │                   └─────────┬─────────┘   │
                                     └─────────────────────────────┼─────────────┘
                                                                   │
                                                    Google Sheets API v4
                                                                   │
                                                        ┌──────────▼──────────┐
                                                        │   Google Sheets     │
                                                        │                     │
                                                        │  📄 收入紀錄         │
                                                        │  📄 支出紀錄         │
                                                        │  📄 固定分配         │
                                                        │  📄 訂閱管理         │
                                                        │  📄 月份總表         │
                                                        └─────────────────────┘
```

### 架構說明

| 元件 | 角色 | 說明 |
|------|------|------|
| **LINE Messaging API** | 訊息入口 | 接收使用者文字訊息，透過 Webhook 轉發至 Backend |
| **Nginx** | 反向代理 | 處理 SSL 終端（Let's Encrypt）、轉發請求至 Python App |
| **Python App** | 核心邏輯 | 解析記帳指令、CRUD Google Sheets、提供 Dashboard REST API |
| **Google Sheets** | 資料庫 | 儲存所有收支紀錄，利用試算表本身的公式輔助統計 |
| **Web Dashboard** | 前端展示 | 讀取 API 資料，渲染圖表與表格 |

---

## Dashboard 功能模組

前端 Dashboard 包含以下核心模組，對應財務管理的各個面向：

### 1. 收入紀錄模組

展示當月及歷史收入明細，包含收入名稱、日期、類型（固定收入/模板/獎金/接案/網拍）、金額，並支援按月份篩選及收入分類檢視。

### 2. 營收結構分析

以**環形圖（Donut Chart）**呈現當月營收佔比，清楚顯示各收入來源的比例，例如：公司薪資、模板銷售、接案、婚禮攝影、二手傢俱拍賣等。支援切換「當月營收佔比」與「收入分佈總表」。

### 3. 月份總表

彙整每月總收入與收入來源標籤，讓使用者快速回顧過去的收入歷史與趨勢。

### 4. 財務分配概覽

以**水平長條圖（Horizontal Bar Chart）**呈現預算分配狀況，依據固定比例分配至：

- 娛樂（10%）
- 教育（10%）
- 生活支出（60%）
- 財務自由（10%）
- 長期儲蓄（10%）

### 5. 固定收入試算 / 當月真實收入

左右分頁切換，顯示預設的固定收入分配試算（理想值）與當月實際到帳的真實收入對比。

### 6. 生活開銷預估

詳細拆解生活支出預算，包含：

- **必要與固定開銷**：租屋、水電瓦斯、網路
- **餐費精算**：每日基礎配額，拆分三餐標準
- **彈性預算**：生活用品、聚餐等非固定支出
- **財務紀律紅線**：觸發條件與消費禁令機制

### 7. 月度營收趨勢圖

以**折線圖（Line Chart）**呈現近 6 個月的營收變化趨勢，輔助判斷收入是否穩定成長。

### 8. 串流訂閱費用

以**環形圖（Donut Chart）**呈現每月訂閱服務的花費分佈，包含 Spotify、Netflix、Notion、Gemini、Perplexity Pro 等服務的金額與佔比。

---

## 技術棧

### Backend

| 技術 | 用途 |
|------|------|
| **Python 3.11+** | 主要開發語言 |
| **FastAPI** | Web 框架，處理 Webhook 及 REST API |
| **line-bot-sdk** | LINE Messaging API 官方 Python SDK |
| **gspread** + **google-auth** | Google Sheets API 操作 |
| **Uvicorn** / **Gunicorn** | ASGI Server（正式環境建議 Gunicorn + Uvicorn Worker） |
| **Nginx** | 反向代理 + SSL 終端 |
| **Let's Encrypt (Certbot)** | 免費 SSL 憑證 |

### Frontend

| 技術 | 用途 |
|------|------|
| **React** 或 **Vue 3** | 前端 SPA 框架 |
| **Chart.js** 或 **Recharts** | 圖表渲染（環形圖、折線圖、長條圖） |
| **Tailwind CSS** | UI 樣式框架 |
| **Axios** 或 **Fetch API** | 與 Backend API 通訊 |

### Infrastructure

| 技術 | 用途 |
|------|------|
| **GCP Compute Engine** | e2-micro 免費 VM（0.25 vCPU / 1 GB RAM） |
| **Google Sheets** | 資料儲存層（取代傳統資料庫） |
| **Systemd** | Python App 常駐服務管理 |
| **GitHub Actions**（選用） | CI/CD 自動部署 |

---

## 運作流程

### 流程一：LINE Bot 記帳

```
使用者在 LINE 輸入訊息
        │
        ▼
LINE Platform 發送 Webhook POST 到 Backend
        │
        ▼
Backend 接收並驗證簽章（X-Line-Signature）
        │
        ▼
訊息解析引擎判斷指令類型
        │
        ├──▶ 記收入：解析「名稱 / 類型 / 金額」寫入 Google Sheets「收入紀錄」工作表
        ├──▶ 記支出：解析「分類 / 品項 / 金額」寫入 Google Sheets「支出紀錄」工作表
        ├──▶ 查詢：讀取 Google Sheets 回傳當月摘要
        └──▶ 未知指令：回覆使用說明
        │
        ▼
透過 LINE Reply API 回覆記帳結果給使用者
```

### 流程二：Dashboard 資料展示

```
使用者開啟 Dashboard 網頁
        │
        ▼
前端發送 API 請求至 Backend
        │
        ├──▶ GET /api/income?month=2026-03       → 當月收入紀錄
        ├──▶ GET /api/expense?month=2026-03      → 當月支出紀錄
        ├──▶ GET /api/summary/monthly             → 月份總表
        ├──▶ GET /api/summary/allocation           → 財務分配數據
        ├──▶ GET /api/summary/trend                → 月度營收趨勢
        └──▶ GET /api/subscriptions                → 訂閱費用清單
        │
        ▼
Backend 讀取 Google Sheets 資料，整理後回傳 JSON
        │
        ▼
前端接收 JSON，渲染圖表與表格
```

### 流程三：資料同步機制

```
Google Sheets 作為 Single Source of Truth
        │
        ├──▶ LINE Bot 寫入 → Sheets 即時更新
        ├──▶ Dashboard 讀取 → 每次載入時從 Sheets 拉取最新資料
        └──▶ 手動編輯 Sheets → Dashboard 下次載入時自動反映
```

---

## 資料結構設計

### Google Sheets 工作表規劃

#### 工作表 1：收入紀錄

| 欄位 | 型別 | 範例 | 說明 |
|------|------|------|------|
| 名稱 | string | Z 公司 - 約聘 | 收入來源名稱 |
| 收入日期 | date | 2026/03/10 | 入帳日期 |
| 收入種類 | string | 固定收入 | 固定收入 / 模板 / 獎金 / 接案 / 網拍 |
| 收入金額 | number | 15000 | 金額（新台幣） |
| 月份總表 | string | 2026-03 | 所屬月份（用於篩選） |

#### 工作表 2：支出紀錄

| 欄位 | 型別 | 範例 | 說明 |
|------|------|------|------|
| Date | date | 2025/9/14 | 消費日期 |
| Type | string | Food | Baby / Food / Drink / Tuition / Other |
| Detail | string | 拉亞+M | 消費品項描述 |
| Amount | number | 415 | 結帳總金額 |
| Payer | string | T | 實際結帳者，`T` 或 `F` |
| T_paid | number | 248 | T 實際負擔金額 |
| F_paid | number | 167 | F 實際負擔金額 |

#### 工作表 3：固定分配設定

| 欄位 | 型別 | 範例 | 說明 |
|------|------|------|------|
| 名稱 | string | 生活支出 | 分配項目 |
| 固定分配金額 | number | 18000 | 預設分配金額 |
| 分配比例 | number | 60 | 百分比 |
| 說明 | string | 支付房租、水電... | 項目描述 |

#### 工作表 4：訂閱管理

| 欄位 | 型別 | 範例 | 說明 |
|------|------|------|------|
| 服務名稱 | string | Spotify | 訂閱服務名 |
| 每月費用 | number | 149 | 月繳金額 |
| 計費週期 | string | 月繳 | 月繳 / 年繳 |
| 狀態 | string | 啟用 | 啟用 / 已取消 |

---

## 部署環境

### GCP Free Tier VM 規格

| 項目 | 規格 |
|------|------|
| 機型 | e2-micro（0.25 shared vCPU） |
| 記憶體 | 1 GB |
| 磁碟 | 30 GB pd-standard |
| 作業系統 | Debian 12 / Ubuntu 24.04 LTS |
| 區域 | us-west1 / us-central1 / us-east1 |
| 網路傳出 | 1 GB / 月（免費額度） |
| SSL | Let's Encrypt（免費） |

### 記憶體分配建議

| 元件 | 預估記憶體 |
|------|-----------|
| OS + Systemd | ~200 MB |
| Nginx | ~30 MB |
| Python App（2 workers） | ~150 MB |
| Swap 緩衝 | 1 GB（磁碟） |
| 可用餘量 | ~620 MB |

### 防火牆規則

| 規則 | 協定 | Port | 來源 |
|------|------|------|------|
| allow-http | TCP | 80 | 0.0.0.0/0 |
| allow-https | TCP | 443 | 0.0.0.0/0 |
| allow-ssh | TCP | 22 | 你的 IP |

---

## 安裝與設定

### 前置準備

1. 申請 [LINE Developers](https://developers.line.biz/) 帳號，建立 Messaging API Channel
2. 取得 `CHANNEL_SECRET` 與 `CHANNEL_ACCESS_TOKEN`
3. 建立 [Google Cloud 專案](https://console.cloud.google.com/)，啟用 Google Sheets API
4. 建立 Service Account，下載金鑰 JSON 檔案
5. 建立 Google Sheets 試算表，將 Service Account Email 加入共用

### 本機開發啟動

#### Backend（FastAPI）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

環境切換（開發 / 正式）：

```powershell
# 開發模式（讀取 backend/.env + backend/.env.development）
$env:APP_ENV="development"
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 正式模式（讀取 backend/.env + backend/.env.production）
$env:APP_ENV="production"
uvicorn main:app --host 0.0.0.0 --port 8000
```

建議先複製範本：

```powershell
copy backend\.env.development.example backend\.env.development
copy backend\.env.production.example backend\.env.production
```

CMD 環境可使用：

```cmd
cd /d C:\Users\2510094\Desktop\tussuhan_project\backend
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

後端啟動後可開啟：

- API Health Check：`http://localhost:8000/health`
- FastAPI Swagger Docs：`http://localhost:8000/docs`
- Dashboard API：`http://localhost:8000/api/dashboard?month=2026-04`

#### Frontend（Vue + Vite）

```powershell
cd frontend
npm install
npm run dev:development
```

前端模式切換（已內建）：

```powershell
# 開發模式（讀取 frontend/.env.development）
npm run dev:development

# 以 production 變數啟動本機（驗證正式參數）
npm run dev:production

# 正式打包（讀取 frontend/.env.production）
npm run build:production
```

前端預設開發網址為 `http://localhost:3000`。若要預覽 production build：

```powershell
cd frontend
npm run build:production
npm run preview
```

### VM 環境初始化

```bash
# 1. 系統更新
sudo apt update && sudo apt upgrade -y

# 2. 安裝 Python 及 Nginx
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# 3. 建立專案目錄
mkdir -p ~/line-bot-accounting && cd ~/line-bot-accounting

# 4. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 5. 安裝 Python 套件
pip install -r backend/requirements.txt
```

### 環境變數設定

```bash
# /etc/environment 或 .env 檔案
APP_ENV=production
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_PATH=/home/your_user/credentials.json
CORS_ORIGIN=https://your-frontend-domain.com
```

若未設定 `GOOGLE_SHEETS_ID` 與 `GOOGLE_CREDENTIALS_PATH`，後端會先回傳 demo data，方便前端開發。設定後會透過 Google Sheets API 讀取試算表資料。

> `CORS_ORIGIN` 支援多個來源（逗號分隔），例如：`http://localhost:3000,https://your-frontend.ngrok-free.dev`。

#### CMD 暫時測試環境變數

```cmd
cd /d C:\Users\2510094\Desktop\tussuhan_project\backend

set GOOGLE_SHEETS_ID=104yNlgh-PwPoQXqBUDIVAehjn-qOQXx7b8Dhgqy0RzY
set GOOGLE_CREDENTIALS_PATH=C:\Users\2510094\Desktop\tussuhan_project\backend\credentials.json
set CORS_ORIGIN=http://localhost:3000
```

確認設定：

```cmd
echo %GOOGLE_SHEETS_ID%
echo %GOOGLE_CREDENTIALS_PATH%
echo %CORS_ORIGIN%
```

`set` 只會套用在目前 CMD 視窗；關閉視窗後需重新設定。

### Google Sheets API 測試

#### 1. Health Check

啟動後端後開啟：

```text
http://localhost:8000/health
```

成功串接 Google Sheets 時應回傳：

```json
{"status":"ok","source":"google_sheets"}
```

#### 2. 模擬 LINE Bot 記帳指令

T 付全額：

```cmd
curl -X POST http://localhost:8000/api/expense/command -H "Content-Type: application/json" -d "{\"text\":\"記 餐費 拉亞+M 415\"}"
```

F 付全額：

```cmd
curl -X POST http://localhost:8000/api/expense/command -H "Content-Type: application/json" -d "{\"text\":\"記F 飲料 coco 99\"}"
```

分帳：

```cmd
curl -X POST http://localhost:8000/api/expense/command -H "Content-Type: application/json" -d "{\"text\":\"記 餐費 早餐+吉品+便當 590 分215\"}"
```

成功後，Google Sheet 的 `支出紀錄` 分頁會新增資料，欄位格式如下：

```text
Date | Type | Detail | Amount | Payer | T_paid | F_paid
```

#### 3. 常見錯誤

- `APIError: [400]: This operation is not supported for this document`：文件不是原生 Google Sheets，需到 `檔案 -> 另存為 Google 試算表` 後改用新的 Sheet ID。
- `WorksheetNotFound: 支出紀錄`：找不到工作表分頁，請把底部分頁改名為 `支出紀錄`，或設定 `EXPENSE_SHEET_NAME=你的分頁名稱`。
- `/health` 回傳 `source=demo`：後端沒有讀到 `GOOGLE_SHEETS_ID` 或 `GOOGLE_CREDENTIALS_PATH`，請在同一個 CMD 視窗設定環境變數後重啟後端。

### Nginx 設定

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 申請 SSL 憑證
sudo certbot --nginx -d your-domain.com
```

### Systemd 服務設定

```ini
# /etc/systemd/system/linebot.service
[Unit]
Description=LINE Bot Accounting Service
After=network.target

[Service]
User=your_user
WorkingDirectory=/home/your_user/line-bot-accounting/backend
ExecStart=/home/your_user/line-bot-accounting/venv/bin/gunicorn \
    main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 127.0.0.1:8000
Restart=always
EnvironmentFile=/home/your_user/line-bot-accounting/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable linebot
sudo systemctl start linebot
```

---

## LINE Bot 指令格式（新版）

> 完整說明頁面可在 Web Dashboard 側邊選單「Bot 指令說明」查看。

### 記帳指令

每個欄位以空白分隔，品項可用 `+` 連接多個名稱，金額只接受正整數。

| 指令格式 | 範例 | 說明 |
|---------|------|------|
| `[品項] [金額]` | `拉亞+M 415` | 極簡記帳。自動推測分類、預設 `T` 付全額、日期為今日 |
| `F [品項] [金額]` | `F coco 99` | F 付全額。`Payer=F`, `T_paid=0`, `F_paid=金額` |
| `[品項] [金額] 分[對方負擔金額]` | `早餐+便當 590 分215` | `分X` 永遠代表對方負擔 X。此例 `T_paid=375`, `F_paid=215` |
| `[類別] [品項] [金額]` | `餐費 拉亞 415` / `Drink 手搖杯 65` | 手動指定分類（中英都可） |
| `[日期] [F]? [品項] [金額] [分X]?` | `昨天 拉亞 415` / `5/7 F 聚餐 600 分300` | 補記日期（日期需放最前面） |
| `記 ...` / `記F ...` | `記 餐費 拉亞+M 415` | 舊版語法仍可使用（相容） |
| `多筆（換行）` | `拉亞 415` + 換行 + `F coco 99` | 一次送多筆，逐筆解析與寫入 |
| `多筆（分號）` | `拉亞 415; F coco 99; 早餐+便當 590 分215` | 支援 `;` 與 `；` 分隔多筆 |

### 日期補記規則

- 支援：`昨天`、`前天`、`M/D`、`YYYY/M/D`
- 日期不可為未來，且不可早於 30 天前

### 查詢與操作指令

| 指令 | 範例 | 說明 |
|------|------|------|
| `查` | `查` | 本月摘要（總支出、T/F 負擔、結算） |
| `查 [YYYY-MM]` / `查 [4月]` | `查 2026-04` / `查 4月` | 指定月份摘要 |
| `查 [分類]` | `查 餐費` | 本月分類小計 |
| `今日` / `昨天` | `昨天` | 該日支出明細 |
| `本月` | `本月` | 同 `查` |
| `最近` / `最近5` | `最近8` | 最近 N 筆紀錄（1~20，預設 5） |
| `結算` | `結算` | 本月誰該補誰 |
| `刪` / `撤銷` | `刪` | 刪除最新一筆紀錄（安全限制） |
| `help` / `說明` / `幫助` / `指令` | `help` | 顯示完整指令清單（記帳 / 查詢 / 操作） |
| `記帳` / `單筆` | `單筆` | 顯示單筆記帳教學與範例 |
| `多筆` | `多筆` | 顯示多筆記帳教學（換行或 `;` / `；` 分隔） |

### 分類對照表

| 輸入關鍵字 | 對應分類 |
|-----------|---------|
| 餐費 / 食物 / 早餐 / 午餐 / 晚餐 | `Food` |
| 飲料 / 喝 | `Drink` |
| 寶寶 / 嬰兒 / 育兒 | `Baby` |
| 學費 / 補習 | `Tuition` |
| 保險 / 保費 | `Insurance` |
| 其他（或直接輸入英文分類名） | `Other` |

### 記帳回覆範例

```
✅ 已記錄
📅 2026/5/8  Food  早餐+便當  $590 (T付)
分擔：T $375 / F $215

📊 2026-05累計
T $12,715
F $2,315
合計 $15,030
```

### 多筆記帳回覆範例

```
✅ 已批次記錄 3 筆（合計 $1104）
1. 2026/5/8 food 拉亞 $415 (T付)
2. 2026/5/8 drink coco $99 (F付)
3. 2026/5/8 food 早餐+便當 $590 (T付)

📊 2026-05累計：T $12,715 / F $2,315 / 合計 $15,030
```

> 若第 N 筆格式錯誤，會回覆：`第 N 筆格式錯誤：...`。  
> 多筆跨月補記時，會分月份顯示各自累計。

### LINE Developers Webhook 設定

部署後將 LINE Developers 後台的 Webhook URL 設為：

```text
https://your-domain.com/webhook
```

後端使用 `LINE_CHANNEL_SECRET` 驗證 `X-Line-Signature`，並透過 `LINE_CHANNEL_ACCESS_TOKEN` 回覆訊息。

---

## 開發規劃

### Phase 1 — MVP（核心功能）

- [ ] LINE Bot Webhook 建置與訊息接收
- [ ] 基本記帳指令解析（記支出 / 記收入）
- [ ] Google Sheets 讀寫串接
- [ ] GCP VM 部署 + SSL + 域名

### Phase 2 — Dashboard 前端

- [ ] Dashboard 版面建構（參考 Notion 風格深色主題）
- [ ] 收入紀錄表格元件
- [ ] 營收結構環形圖（Donut Chart）
- [ ] 月度營收趨勢折線圖（Line Chart）
- [ ] 財務分配水平長條圖（Horizontal Bar Chart）
- [ ] 訂閱費用環形圖

### Phase 3 — 進階功能

- [ ] 月份總表自動彙整
- [ ] 固定分配 vs 實際收入對比
- [ ] 生活開銷預估與紅線警示
- [ ] 彈性預算追蹤
- [ ] Dashboard 驗證機制（簡易 Token 或 LINE Login）

### Phase 4 — 優化與擴展

- [ ] 加入快取機制（減少 Sheets API 呼叫）
- [ ] LINE Flex Message 美化回覆
- [ ] LIFF（LINE Front-end Framework）整合 Dashboard
- [ ] 每月自動摘要推送
- [ ] 資料匯出功能（CSV / PDF）

---

## 專案結構

```
line-bot-accounting/
├── backend/
│   ├── main.py             # FastAPI 主程式
│   ├── app.py              # FastAPI app 相容匯出
│   ├── config.py           # 環境變數與設定
│   ├── requirements.txt    # Python 套件清單
│   ├── sheets_client.py    # Google Sheets 連線與資料轉換
│   ├── services.py         # Dashboard 統計與彙整
│   ├── expense_parser.py   # 支出記帳與分帳指令解析
│   ├── demo_data.py        # 未設定 Sheets 時的開發資料
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py # FastAPI dependency injection
│       └── routes.py       # Dashboard REST API 端點
│
├── .env                    # 環境變數（不入版控）
├── credentials.json        # Google Service Account 金鑰（不入版控）
│
├── frontend/               # Dashboard 前端（獨立建置）
│   ├── src/
│   │   ├── components/
│   │   │   ├── IncomeTable.jsx
│   │   │   ├── RevenueDonut.jsx
│   │   │   ├── TrendLineChart.jsx
│   │   │   ├── AllocationBar.jsx
│   │   │   ├── SubscriptionDonut.jsx
│   │   │   └── BudgetBreakdown.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── deploy/
│   ├── nginx.conf          # Nginx 設定檔
│   └── linebot.service     # Systemd 服務檔
│
└── README.md
```

---

## License

MIT License

---

> 💡 **提示**：此系統設計以 Google Sheets 作為輕量資料庫，適合個人或小規模使用。若未來資料量增長，可考慮遷移至 SQLite 或 PostgreSQL。