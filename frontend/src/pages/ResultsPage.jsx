import { useCallback, useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { shortHash } from '../lib/ui.jsx'

export default function ResultsPage() {
  const [records, setRecords] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [onlyFlagged, setOnlyFlagged] = useState(true)
  const [selected, setSelected] = useState(null)
  const [certificate, setCertificate] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.listResults({ only_flagged: onlyFlagged, limit: 300 })
      setRecords(result.records)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [onlyFlagged])

  useEffect(() => {
    load()
  }, [load])

  const runOfficial = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.loadOfficialResults()
      setSummary(result)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const openCertificate = async (puId) => {
    setSelected(puId)
    setCertificate(null)
    try {
      setCertificate(await api.certificate(puId))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <div className="page-intro">
        <p className="page-intro__eyebrow">Result checks</p>
        <h1>Arithmetic that anyone can re-check with a pen</h1>
        <p className="page-intro__lede">
          These checks compare a record against objective rules — whether the sheet's own
          numbers close, and whether accreditation exceeds the register. They produce flags for a
          reviewer. They never conclude that a result is wrong, and they never name a winner.
        </p>
      </div>

      <div className="notice notice--info">
        <h3>Two tiers, deliberately</h3>
        <p>
          <strong>Structural</strong> findings are arithmetic contradictions that cannot both be
          true on a correct sheet. <strong>Advisory</strong> findings are statistical hints —
          round numbers, digit patterns, turnout outliers — that the official brief warns will
          over-fire. Advisory findings are labelled as such and never carry the same weight.
        </p>
      </div>

      <div className="queue-head">
        <div className="filters">
          <div>
            <label htmlFor="r-filter">Show</label>
            <select id="r-filter" value={String(onlyFlagged)} onChange={(e) => setOnlyFlagged(e.target.value === 'true')}>
              <option value="true">Flagged records only</option>
              <option value="false">All records</option>
            </select>
          </div>
        </div>
        <button className="btn btn--signal" onClick={runOfficial} disabled={loading}>
          {loading ? 'Working…' : 'Run checks on the official synthetic pack (900 units)'}
        </button>
      </div>

      {error && (
        <div className="verify-panel verify-panel--bad" role="alert" style={{ marginBottom: 'var(--s4)' }}>
          {error}
        </div>
      )}

      {summary && (
        <div className="stat-row">
          <div className="stat">
            <span className="stat__n">{summary.ingested}</span>
            <span className="stat__k">Records checked</span>
          </div>
          <div className="stat">
            <span className="stat__n">{summary.flagged}</span>
            <span className="stat__k">Flagged</span>
          </div>
          <div className="stat">
            <span className="stat__n">{(summary.flag_rate * 100).toFixed(1)}%</span>
            <span className="stat__k">Flag rate</span>
          </div>
          <div className="stat">
            <span className="stat__n">{summary.checks_run.length}</span>
            <span className="stat__k">Rules run per record</span>
          </div>
        </div>
      )}

      {records.length === 0 && !loading && (
        <div className="empty">
          <h3>No records loaded yet</h3>
          <p>
            Run the checks on the official synthetic pack, or POST records to{' '}
            <span className="mono">/v1/results/check</span>.
          </p>
        </div>
      )}

      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {records.map((record) => (
          <li key={record.id} className="record">
            <div className="record__top">
              <div style={{ display: 'flex', gap: 'var(--s2)', flexWrap: 'wrap', alignItems: 'center' }}>
                <span className="badge badge--neutral mono">{record.pu_id}</span>
                {record.rule_report.structural_count > 0 && (
                  <span className="badge badge--structural">
                    {record.rule_report.structural_count} structural
                  </span>
                )}
                {record.rule_report.advisory_count > 0 && (
                  <span className="badge badge--advisory">
                    {record.rule_report.advisory_count} advisory
                  </span>
                )}
                {record.rule_report.findings.length === 0 && <span className="badge badge--ok">consistent</span>}
              </div>
              <span className="record__id">{shortHash(record.content_hash, 12, 8)}</span>
            </div>

            <div className="record__meta" style={{ marginBottom: 'var(--s3)' }}>
              <span>registered: {record.registered_voters}</span>
              <span>accredited: {record.accredited_voters}</span>
              <span>rejected: {record.rejected_votes}</span>
              <span>
                votes: {Object.entries(record.votes).map(([k, v]) => `${k}=${v}`).join(' ')}
              </span>
            </div>

            {record.rule_report.findings.length > 0 && (
              <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                {record.rule_report.findings.map((f) => (
                  <li key={f.rule} style={{ marginBottom: 'var(--s2)' }}>
                    <span className={`badge badge--${f.tier === 'structural' ? 'structural' : 'advisory'}`}>
                      {f.tier}
                    </span>{' '}
                    {f.message}
                    {f.benign_explanations?.length > 0 && (
                      <details className="disclosure" style={{ marginTop: 'var(--s2)' }}>
                        <summary>Plausible innocent explanations to rule out first</summary>
                        <ul style={{ margin: 'var(--s3) 0 0', paddingLeft: '1.1rem' }}>
                          {f.benign_explanations.map((b) => (
                            <li key={b}>{b}</li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </li>
                ))}
              </ul>
            )}

            <button className="btn btn--ghost btn--sm" style={{ marginTop: 'var(--s3)' }} onClick={() => openCertificate(record.pu_id)}>
              Show arithmetic certificate
            </button>

            {selected === record.pu_id && (
              <div style={{ marginTop: 'var(--s4)' }}>
                {!certificate && <div className="skeleton" style={{ width: '70%' }} />}
                {certificate && <Certificate cert={certificate} />}
              </div>
            )}
          </li>
        ))}
      </ul>
    </>
  )
}

function Certificate({ cert }) {
  return (
    <div className="card" style={{ padding: 'var(--s4)' }}>
      <h3 style={{ fontSize: '0.95rem' }}>Arithmetic certificate — {cert.pu_id}</h3>
      <p className="field__hint">{cert.method}</p>
      <table className="cert">
        <thead>
          <tr>
            <th scope="col">Identity</th>
            <th scope="col">Left</th>
            <th scope="col">Right</th>
            <th scope="col">Balances</th>
          </tr>
        </thead>
        <tbody>
          {cert.lines.map((line) => (
            <tr key={line.identity}>
              <td>
                {line.identity}
                <br />
                <span className="field__hint">{line.note}</span>
              </td>
              <td>{line.left}</td>
              <td>{line.right}</td>
              <td className={line.balances ? 'cert__yes' : 'cert__no'}>
                {line.balances ? 'yes' : 'NO'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{ marginTop: 'var(--s3)', marginBottom: 0 }}>
        Overall:{' '}
        <strong className={cert.all_balance ? 'cert__yes' : 'cert__no'}>
          {cert.all_balance ? 'all identities balance' : 'at least one identity does not balance'}
        </strong>
      </p>
    </div>
  )
}
