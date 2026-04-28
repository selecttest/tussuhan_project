const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchDashboardData(month) {
    const url = new URL('/api/dashboard', API_BASE_URL);
    if (month) {
        url.searchParams.set('month', month);
    }

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }

    return response.json();
}

export async function fetchAllExpenseRecords() {
    const url = new URL('/api/expense/all', API_BASE_URL);
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }
    return response.json();
}

export async function fetchExpenseRecords(month) {
    const url = new URL('/api/expense', API_BASE_URL);
    if (month) {
        url.searchParams.set('month', month);
    }
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`後端回應錯誤：${response.status}`);
    }
    return response.json();
}
