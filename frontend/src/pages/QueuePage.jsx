import { useCallback, useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import {
  BandBadge,
  CATEGORY_LABEL,
  DECISION_LABEL,
  SeverityBar,
  SEVERITY_LABEL,
  formatTime,
  shortHash,
} from '../lib/ui.jsx'

const DECISIONS = Object.keys(DECISION_LABEL)

export default function QueuePage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({ band: '', review_state: 'pending', category: '' })
  const [expanded, setExpanded] = useState(null)
  const [detail, setDetail] = useState({})
  const [reviewing, setReviewing] = useState(null)
  const [stats, setStats] = useState(null)
  const [clusters, setClusters] = useState([])

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [list, s, c] = await Promise.all([
        api.listReports({ ...filters, limit: 50 }),
        api.stats(),
        api.clusters(8),
      ])
      setReports(list.reports)
      setStats(s)
      setClusters(c.clusters)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    load()
  }, [load])

  const openDetail = async (id) => {
    if (expanded === id) {
      setExpanded(null)
      return
    }
    setExpanded(id)
    if (!detail[id]) {
      try {
        const [report, explanation] = await Promise.all([api.getReport(id), api.explainReport(id)])
        setDetail((d) => ({ ...d, [id]: { report, explanation } }))
      } catch (err) {
        setError(err.message)
      }
    }
  }

  const submitReview = async (id, form) => {
    setError('')
    try {
      await api.reviewReport(id, form)
      setReviewing(null)
      setDetail((d) => {
        const next = { ...d }
        delete next[id]
        return next
      })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <div className="page-intro">
        <p className="page-intro__eyebrow">Reviewer queue</p>
        <h1>Everything here is a question, not a conclusion</h1>
        <p className="page-intro__lede">
          Reports are ordered by a published weighted model so the riskiest reach a human first.
          Every decision requires a reason and is written to the audit log.
        </p>
      </div>

      {stats && (
        <div className="stat-row">
          <div className="stat">
            <span className="stat__n">{stats.reports}</span>
            <span className="stat__k">Reports held</span>
          </div>
          <div className="stat">
            <span className="stat__n">{stats.reports_pending}</span>
            <span className="stat__k">Awaiting review</span>
          </div>
          <div className="stat">
            <span className="stat__n">{stats.reports_reviewed}</span>
            <span className="stat__k">Reviewed</span>
          </div>
          <div className="stat">
            <span className="stat__n">{stats.audit_entries}</span>
            <span className="stat__k">Audit entries</span>
          </div>
          <div className="stat">
            <span className="stat__n">{stats.clusters}</span>
            <span className="stat__k">Report clusters</span>
          </div>
        </div>
      )}

      <div className="queue-head">
        <div className="filters">
          <div>
            <label htmlFor="f-band">Priority</label>
            <select
              id="f-band"
              value={filters.band}
              onChange={(e) => setFilters((f) => ({ ...f, band: e.target.value }))}
            >
              <option value="">All</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="routine">Routine</option>
            </select>
          </div>
          <div>
            <label htmlFor="f-state">Review state</label>
            <select
              id="f-state"
              value={filters.review_state}
              onChange={(e) => setFilters((f) => ({ ...f, review_state: e.target.value }))}
            >
              <option value="pending">Pending</option>
              <option value="reviewed">Reviewed</option>
              <option value="">All</option>
            </select>
          </div>
          <div>
            <label htmlFor="f-category">Category</label>
            <select
              id="f-category"
              value={filters.category}
              onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
            >
              <option value="">All</option>
              {Object.entries(CATEGORY_LABEL).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button className="btn btn--ghost btn--sm" onClick={load} disabled={loading}>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="verify-panel verify-panel--bad" role="alert" style={{ marginBottom: 'var(--s4)' }}>
          {error}
        </div>
      )}

      {loading && reports.length === 0 && (
        <div className="card">
          <div className="skeleton" style={{ width: '60%', marginBottom: 'var(--s3)' }} />
          <div className="skeleton" style={{ width: '90%', marginBottom: 'var(--s3)' }} />
          <div className="skeleton" style={{ width: '40%' }} />
        </div>
      )}

      {!loading && reports.length === 0 && (
        <div className="empty">
          <h3>Nothing in the queue</h3>
          <p>
            File a report from the “File a report” tab and it will appear here, ordered for a
            human reviewer.
          </p>
        </div>
      )}

      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {reports.map((report) => (
          <li key={report.id} className={`record record--${report.priority_band}`}>
            <div className="record__top">
              <div style={{ display: 'flex', gap: 'var(--s2)', alignItems: 'center', flexWrap: 'wrap' }}>
                <BandBadge band={report.priority_band} />
                <span className="badge badge--neutral">{CATEGORY_LABEL[report.category] || report.category}</span>
                {report.is_sensitive && <span className="badge badge--urgent">Sensitive handling</span>}
                {report.has_evidence && <span className="badge badge--ok">Evidence attached</span>}
                {report.cluster_id && (
                  <span className="badge badge--neutral">cluster {shortHash(report.cluster_id, 4, 3)}</span>
                )}
              </div>
              <span className="record__id">{report.id}</span>
            </div>

            <p className="record__body">{report.narrative}</p>

            <div className="record__meta">
              <span>state: {report.state}</span>
              {report.pu_id && <span>unit: {report.pu_id}</span>}
              <span>reported severity: {report.severity_reported ?? '—'}</span>
              <span>
                assist: {report.severity_estimated ?? 'abstained'}
                {report.severity_confidence ? ` (${Math.round(report.severity_confidence * 100)}%)` : ''}
              </span>
              <span>priority: {report.priority}</span>
              <span>{formatTime(report.created_at)}</span>
            </div>

            <div style={{ marginTop: 'var(--s3)', display: 'flex', gap: 'var(--s3)', flexWrap: 'wrap' }}>
              <button className="btn btn--ghost btn--sm" onClick={() => openDetail(report.id)} aria-expanded={expanded === report.id}>
                {expanded === report.id ? 'Hide' : 'Open'} record
              </button>
              <button className="btn btn--sm" onClick={() => setReviewing(reviewing === report.id ? null : report.id)}>
                Record a decision
              </button>
            </div>

            {expanded === report.id && (
              <div style={{ marginTop: 'var(--s4)' }}>
                {!detail[report.id] && <div className="skeleton" style={{ width: '70%' }} />}
                {detail[report.id] && (
                  <>
                    <h3 style={{ fontSize: '0.95rem', marginBottom: 'var(--s2)' }}>Why this was ranked here</h3>
                    <ul style={{ margin: '0 0 var(--s3)', paddingLeft: '1.1rem' }}>
                      {detail[report.id].explanation.triage_rationale.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                    <h3 style={{ fontSize: '0.95rem', marginBottom: 'var(--s2)' }}>Score contributions</h3>
                    <table className="cert">
                      <thead>
                        <tr>
                          <th scope="col">Signal</th>
                          <th scope="col">Weighted contribution</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(report.triage.contributions || {}).map(([k, v]) => (
                          <tr key={k}>
                            <td>{k}</td>
                            <td>{v}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="field__hint">
                      Weights are published in the About tab. A reviewer may disagree with any of
                      them; the ordering is an aid, not a finding.
                    </p>
                    <h3 style={{ fontSize: '0.95rem', margin: 'var(--s3) 0 var(--s2)' }}>Evidence integrity</h3>
                    <span className="hashline">content sha256: {report.content_hash}</span>
                    {report.evidence_sha256 && (
                      <span className="hashline" style={{ marginTop: 'var(--s2)' }}>
                        evidence sha256: {report.evidence_sha256}
                      </span>
                    )}
                  </>
                )}
              </div>
            )}

            {reviewing === report.id && (
              <ReviewForm report={report} onCancel={() => setReviewing(null)} onSubmit={submitReview} />
            )}

            {report.review_actions?.length > 0 && (
              <div style={{ marginTop: 'var(--s3)' }}>
                <h3 style={{ fontSize: '0.9rem' }}>Decisions recorded</h3>
                <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                  {report.review_actions.map((a) => (
                    <li key={a.id}>
                      <strong>{DECISION_LABEL[a.decision] || a.decision}</strong> — {a.reason}{' '}
                      <span className="record__id">
                        ({a.reviewer}, {formatTime(a.created_at)})
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>

      {clusters.length > 0 && (
        <section style={{ marginTop: 'var(--s7)' }}>
          <h2>Repeated reports</h2>
          <p className="page-intro__lede">
            Reports that describe the same thing are grouped, so a reviewer sees one item with a
            count instead of fifty separate entries.
          </p>
          <table className="cert">
            <thead>
              <tr>
                <th scope="col">Cluster</th>
                <th scope="col">Category</th>
                <th scope="col">Reports</th>
                <th scope="col">Example</th>
              </tr>
            </thead>
            <tbody>
              {clusters.map((c) => (
                <tr key={c.cluster_id}>
                  <td>{c.cluster_id}</td>
                  <td>{CATEGORY_LABEL[c.category] || c.category}</td>
                  <td>{c.size}</td>
                  <td>{c.example}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </>
  )
}

function ReviewForm({ report, onCancel, onSubmit }) {
  const [decision, setDecision] = useState('needs_more_evidence')
  const [reviewer, setReviewer] = useState('')
  const [reason, setReason] = useState('')
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)

  const valid = reviewer.trim().length >= 2 && reason.trim().length >= 5

  return (
    <form
      style={{ marginTop: 'var(--s4)', borderTop: '1px solid var(--paper-line)', paddingTop: 'var(--s4)' }}
      onSubmit={async (event) => {
        event.preventDefault()
        setBusy(true)
        await onSubmit(report.id, { reviewer, decision, reason, note: note || null })
        setBusy(false)
      }}
    >
      <div className="grid grid--2">
        <div className="field">
          <label className="field__label" htmlFor={`reviewer-${report.id}`}>
            Reviewer name or handle
          </label>
          <input
            id={`reviewer-${report.id}`}
            type="text"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            required
          />
          <span className="field__hint">Recorded in the audit log against this decision.</span>
        </div>
        <div className="field">
          <label className="field__label" htmlFor={`decision-${report.id}`}>
            Decision
          </label>
          <select id={`decision-${report.id}`} value={decision} onChange={(e) => setDecision(e.target.value)}>
            {DECISIONS.map((d) => (
              <option key={d} value={d}>
                {DECISION_LABEL[d]}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="field">
        <label className="field__label" htmlFor={`reason-${report.id}`}>
          Reason (required)
        </label>
        <textarea
          id={`reason-${report.id}`}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={500}
          style={{ minHeight: 80 }}
          required
          aria-describedby={`reason-hint-${report.id}`}
        />
        <span className="field__hint" id={`reason-hint-${report.id}`}>
          State what you checked and what you concluded. At least 5 characters.
        </span>
      </div>
      <div className="field">
        <label className="field__label" htmlFor={`note-${report.id}`}>
          Internal note (optional)
        </label>
        <input id={`note-${report.id}`} type="text" value={note} onChange={(e) => setNote(e.target.value)} maxLength={1000} />
      </div>
      <div style={{ display: 'flex', gap: 'var(--s3)' }}>
        <button className="btn btn--signal" type="submit" disabled={!valid || busy}>
          {busy ? 'Recording…' : 'Record decision'}
        </button>
        <button className="btn btn--ghost" type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}
