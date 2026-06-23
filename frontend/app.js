const API_BASE = 'http://localhost:8000';

async function apiFetch(path, options = {}) {
    const config = {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    };
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    const res = await fetch(`${API_BASE}${path}`, config);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
}

function showAlert(containerId, type, message) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const icons = { error: '✕', success: '✓', info: 'ℹ' };
    container.innerHTML = `
        <div class="alert alert-${type}">
            <span>${icons[type] || ''}</span>
            <span>${message}</span>
        </div>
    `;
    setTimeout(() => { container.innerHTML = ''; }, 5000);
}

function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) {
        btn.classList.add('loading');
        btn.disabled = true;
    } else {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

function formatCurrency(amount, currency = 'ARS') {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
    }).format(amount);
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('es-AR', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}
