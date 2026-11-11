const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
  } catch {
    throw new Error('Cannot reach the Python API. Start the FastAPI backend on port 8000 and try again.');
  }

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `Request failed (${response.status}).`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return payload;
}

export const api = {
  health: () => request('/api/health'),
  overview: () => request('/api/overview'),
  insights: () => request('/api/insights'),
  performance: () => request('/api/performance'),
  config: () => request('/api/config'),
  predict: (profile) => request('/api/predictions', { method: 'POST', body: JSON.stringify(profile) }),
  history: (limit = 100) => request(`/api/predictions/history?limit=${limit}`),
  prediction: (id) => request(`/api/predictions/${id}`),
  clearHistory: () => request('/api/predictions/history', { method: 'DELETE' }),
};

export function downloadCsv(filename, rows) {
  if (!rows?.length) return;
  const headers = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  const escape = (value) => {
    const text = value == null ? '' : String(value);
    return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  const csv = [headers.join(','), ...rows.map((row) => headers.map((key) => escape(row[key])).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
