INCOME_RECORDS = [
    {"name": "Z公司 - 約聘薪資", "date": "2026/04/10", "type": "固定收入", "amount": 28000, "month": "2026-04"},
    {"name": "Notion 模板銷售", "date": "2026/04/15", "type": "模板", "amount": 3500, "month": "2026-04"},
    {"name": "接案 - 品牌設計", "date": "2026/04/20", "type": "接案", "amount": 6000, "month": "2026-04"},
    {"name": "婚禮攝影", "date": "2026/04/22", "type": "接案", "amount": 4500, "month": "2026-04"},
    {"name": "二手傢俱拍賣", "date": "2026/04/25", "type": "網拍", "amount": 1200, "month": "2026-04"},
    {"name": "Z公司 - 約聘薪資", "date": "2026/03/10", "type": "固定收入", "amount": 28000, "month": "2026-03"},
    {"name": "Notion 模板銷售", "date": "2026/03/18", "type": "模板", "amount": 2800, "month": "2026-03"},
    {"name": "接案 - UI 設計", "date": "2026/03/25", "type": "接案", "amount": 7500, "month": "2026-03"},
    {"name": "接案 - 攝影紀錄", "date": "2026/03/28", "type": "接案", "amount": 4400, "month": "2026-03"},
    {"name": "Z公司 - 約聘薪資", "date": "2026/02/10", "type": "固定收入", "amount": 28000, "month": "2026-02"},
    {"name": "獎金", "date": "2026/02/16", "type": "獎金", "amount": 7000, "month": "2026-02"},
    {"name": "接案 - 品牌顧問", "date": "2026/02/21", "type": "接案", "amount": 9000, "month": "2026-02"},
    {"name": "Z公司 - 約聘薪資", "date": "2026/01/10", "type": "固定收入", "amount": 28000, "month": "2026-01"},
    {"name": "Notion 模板銷售", "date": "2026/01/18", "type": "模板", "amount": 3200, "month": "2026-01"},
    {"name": "接案 - 平面設計", "date": "2026/01/25", "type": "接案", "amount": 5600, "month": "2026-01"},
    {"name": "Z公司 - 約聘薪資", "date": "2025/12/10", "type": "固定收入", "amount": 28000, "month": "2025-12"},
    {"name": "接案 - 攝影紀錄", "date": "2025/12/22", "type": "接案", "amount": 13200, "month": "2025-12"},
    {"name": "Z公司 - 約聘薪資", "date": "2025/11/10", "type": "固定收入", "amount": 28000, "month": "2025-11"},
    {"name": "網拍收入", "date": "2025/11/19", "type": "網拍", "amount": 10500, "month": "2025-11"},
]

EXPENSE_RECORDS = [
    {"date": "2026/04/03", "category": "餐費", "item": "午餐與咖啡", "amount": 3200, "month": "2026-04"},
    {"date": "2026/04/05", "category": "生活支出", "item": "租屋", "amount": 12000, "month": "2026-04"},
    {"date": "2026/04/07", "category": "交通", "item": "捷運與計程車", "amount": 900, "month": "2026-04"},
    {"date": "2026/04/12", "category": "教育", "item": "線上課程", "amount": 3800, "month": "2026-04"},
    {"date": "2026/04/18", "category": "娛樂", "item": "電影與聚餐", "amount": 2160, "month": "2026-04"},
    {"date": "2026/03/05", "category": "生活支出", "item": "租屋", "amount": 12000, "month": "2026-03"},
    {"date": "2026/03/11", "category": "餐費", "item": "餐費彙總", "amount": 4500, "month": "2026-03"},
    {"date": "2026/03/19", "category": "教育", "item": "書籍", "amount": 1800, "month": "2026-03"},
    {"date": "2026/03/23", "category": "娛樂", "item": "聚餐", "amount": 1800, "month": "2026-03"},
    {"date": "2026/02/10", "category": "生活支出", "item": "生活費彙總", "amount": 19800, "month": "2026-02"},
    {"date": "2026/01/10", "category": "生活支出", "item": "生活費彙總", "amount": 17500, "month": "2026-01"},
    {"date": "2025/12/10", "category": "生活支出", "item": "生活費彙總", "amount": 22000, "month": "2025-12"},
    {"date": "2025/11/10", "category": "生活支出", "item": "生活費彙總", "amount": 18200, "month": "2025-11"},
]

ALLOCATIONS = [
    {"label": "生活支出", "pct": 60, "description": "租屋、水電、餐費與日常必要支出"},
    {"label": "財務自由", "pct": 10, "description": "投資與被動收入配置"},
    {"label": "長期儲蓄", "pct": 10, "description": "緊急預備金與中長期目標"},
    {"label": "教育", "pct": 10, "description": "課程、書籍與技能成長"},
    {"label": "娛樂", "pct": 10, "description": "休閒、聚餐與生活體驗"},
]

SUBSCRIPTIONS = [
    {"name": "Gemini", "fee": 650, "cycle": "月繳", "status": "啟用", "icon": "pi-google", "color": "#4285F4"},
    {"name": "Netflix", "fee": 390, "cycle": "月繳", "status": "啟用", "icon": "pi-video", "color": "#E50914"},
    {"name": "Perplexity Pro", "fee": 200, "cycle": "月繳", "status": "啟用", "icon": "pi-search", "color": "#20B2AA"},
    {"name": "Notion", "fee": 150, "cycle": "月繳", "status": "啟用", "icon": "pi-file", "color": "#000000"},
    {"name": "Spotify", "fee": 149, "cycle": "月繳", "status": "啟用", "icon": "pi-volume-up", "color": "#1DB954"},
]
