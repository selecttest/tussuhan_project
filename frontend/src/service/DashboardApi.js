const CONFIGURED_BASE = import.meta.env.VITE_API_BASE_URL;

/**
 * API 根位址。
 * - 有設定 VITE_API_BASE_URL：直接打該後端（正式 build 常用）。
 * - 開發且未設定：用當前網頁來源（例：localhost:3000），由 Vite proxy 轉到記帳後端，避免 8000 已被其他專案占用。
 * - 其餘：預設 http://localhost:8000
 */
function apiOrigin() {
    if (CONFIGURED_BASE != null && String(CONFIGURED_BASE).trim() !== '') {
        return String(CONFIGURED_BASE).replace(/\/$/, '');
    }
    if (import.meta.env.DEV && typeof window !== 'undefined') {
        return window.location.origin;
    }
    return 'http://localhost:8000';
}

function buildUrl(path, searchParams) {
    const url = new URL(path.startsWith('/') ? path : `/${path}`, apiOrigin());
    if (searchParams) {
        for (const [k, v] of Object.entries(searchParams)) {
            if (v != null && v !== '') url.searchParams.set(k, String(v));
        }
    }
    return url.toString();
}

export async function fetchDashboardData(month) {
    const response = await fetch(buildUrl('/api/dashboard', month ? { month } : undefined));
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }

    return response.json();
}

export async function fetchAllExpenseRecords() {
    const response = await fetch(buildUrl('/api/expense/all'));
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }
    return response.json();
}

export async function fetchExpenseRecords(month) {
    const response = await fetch(buildUrl('/api/expense', month ? { month } : undefined));
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }
    return response.json();
}

async function parseApiError(response) {
    try {
        const data = await response.json();
        const d = data.detail;
        if (typeof d === 'string') {
            return d;
        }
        if (Array.isArray(d)) {
            return d.map((x) => (typeof x === 'string' ? x : x.msg || JSON.stringify(x))).join('；');
        }
    } catch {
        /* ignore */
    }
    return `請求失敗（${response.status}）`;
}

export async function updateExpenseRow(sheetRow, body) {
    const response = await fetch(buildUrl(`/api/expense/row/${sheetRow}`), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        throw new Error(await parseApiError(response));
    }
    return response.json();
}

export async function deleteExpenseRow(sheetRow) {
    const response = await fetch(buildUrl(`/api/expense/row/${sheetRow}`), {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error(await parseApiError(response));
    }
    return response.json();
}
