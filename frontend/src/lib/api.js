// Thin API client. Every call goes through one place so error handling, timeouts and the
// offline path are consistent.

const BASE = ''

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'error' } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

async function request(path, { method = 'GET', body, signal } = {}) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
    signal,
  }
  if (body !== undefined) options.body = JSON.stringify(body)

  let response
  try {
    response = await fetch(`${BASE}${path}`, options)
  } catch (error) {
    if (error.name === 'AbortError') throw error
    // A network failure here is the offline case, which the app treats as a first-class state.
    throw new ApiError('Cannot reach the SHAIDA service. Work is kept locally until it returns.', {
      code: 'offline',
    })
  }

  const text = await response.text()
  let payload = null
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = null
    }
  }

  if (!response.ok) {
    const detail = payload?.detail ?? payload?.error?.message
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
          : `Request failed with status ${response.status}`
    throw new ApiError(message, {
      status: response.status,
      code: payload?.error?.code || 'http_error',
    })
  }
  return payload
}

export const api = {
  health: () => request('/v1/health'),
  stats: () => request('/v1/stats'),
  datasets: () => request('/v1/datasets'),

  createReport: (body) => request('/v1/reports', { method: 'POST', body }),
  listReports: (params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''),
    ).toString()
    return request(`/v1/reports${query ? `?${query}` : ''}`)
  },
  getReport: (id) => request(`/v1/reports/${encodeURIComponent(id)}`),
  verifyReport: (id) => request(`/v1/reports/${encodeURIComponent(id)}/verify`),
  explainReport: (id, language = 'en') =>
    request(`/v1/reports/${encodeURIComponent(id)}/explain?language=${language}`),
  reviewReport: (id, body) =>
    request(`/v1/reports/${encodeURIComponent(id)}/review`, { method: 'POST', body }),

  loadOfficialResults: () => request('/v1/results/load-official', { method: 'POST' }),
  listResults: (params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''),
    ).toString()
    return request(`/v1/results${query ? `?${query}` : ''}`)
  },
  certificate: (puId) => request(`/v1/results/${encodeURIComponent(puId)}/certificate`),

  matchClaim: (body) => request('/v1/claims/match', { method: 'POST', body }),

  audit: (limit = 30) => request(`/v1/integrity/audit?limit=${limit}`),
  aggregate: (groupBy = 'state') => request(`/v1/aggregate?group_by=${groupBy}`),
  clusters: (limit = 12) => request(`/v1/clusters?limit=${limit}`),
}
