import { useCallback, useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { formatTime, shortHash } from '../lib/ui.jsx'

export default function IntegrityPage() {
  const [audit, setAudit] = useState(null)
  const [aggregate, setAggregate] = useState(null)
  const [groupBy, setGroupBy] = useState('state')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [auditResult, aggResult] = await Promise.all([api.audit(30), api.aggregate(groupBy)])
      setAudit(auditResult)
      setAggregate(aggResult)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [groupBy])

  useEffect(() => {
    load()
  }, [load])

  return (
    <>
      <div className="page-intro">
        <p className="page-intro__eyebrow">Integrity</p>
        <h1>Anyone can check that the record was not altered</h1>
        <p className="page-intro__lede">
          Every action is appended to a hash chain: each entry commits to the one before it, so
          editing or removing any entry breaks every link after it. Verification is re-computed
          here from the stored data, not trusted from the writer.
        </p>
      </div>

      {error && (
        <div className="verify-panel verify-panel--bad" role="alert" style={{ marginBottom: 'var(--s4)' }}>
          {error}
        </div>
      )}

      {audit && (
        <>
          <div
            className={`verify-panel verify-panel--${audit.intact ? 'ok' : 'bad'}`}
            style={{ marginBottom: 'var(--s5)' }}
            role="status"
          >
            <h3>{audit.intact ? 'Audit chain intact' : 'Audit chain is broken'}</h3>
            <p style={{ margin: 0 }}>
              {audit.entries_checked} entries re-computed. Method: {audit.method}.
            </p>
            {!audit.intact && (
              <p style={{ margin: 0 }}>
                First broken at sequence {audit.first_broken_seq}: {audit.reason}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', gap: 'var(--s3)', marginBottom: 'var(--s3)', flexWrap: 'wrap' }}>
            <button className="btn btn--ghost btn--sm" onClick={load} disabled={loading}>
              {loading ? 'Re-verifying…' : 'Re-verify now'}
            </button>
          </div>

          <h2>Most recent audit entries</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="cert">
              <thead>
                <tr>
                  <th scope="col">Seq</th>
                  <th scope="col">Action</th>
                  <th scope="col">Subject</th>
                  <th scope="col">Actor</th>
                  <th scope="col">Payload hash</th>
                  <th scope="col">Chain hash</th>
                  <th scope="col">When</th>
                </tr>
              </thead>
              <tbody>
                {audit.entries.map((entry) => (
                  <tr key={entry.entry_id}>
                    <td>{entry.seq}</td>
                    <td>{entry.action}</td>
                    <td>
                      {entry.subject_type}
                      <br />
                      <span className="record__id">{shortHash(entry.subject_id, 6, 4)}</span>
                    </td>
                    <td>{entry.actor_role}</td>
                    <td className="mono">{shortHash(entry.payload_hash, 8, 6)}</td>
                    <td className="mono">{shortHash(entry.chain_hash, 8, 6)}</td>
                    <td>{formatTime(entry.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <section style={{ marginTop: 'var(--s7)' }}>
        <h2>Aggregates, with a privacy floor</h2>
        <p className="page-intro__lede">
          Aggregates are only ever produced with a k-anonymity floor. Cells with fewer reports
          than the floor are suppressed entirely — not rounded — so an individual report cannot
          be recovered by subtraction.
        </p>

        <div className="filters" style={{ marginBottom: 'var(--s4)' }}>
          <div>
            <label htmlFor="groupby">Group by</label>
            <select id="groupby" value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
              <option value="state">State</option>
              <option value="category">Category</option>
              <option value="band">Priority band</option>
            </select>
          </div>
        </div>

        {aggregate && (
          <>
            <div className="stat-row">
              <div className="stat">
                <span className="stat__n">{aggregate.groups.length}</span>
                <span className="stat__k">Groups published</span>
              </div>
              <div className="stat">
                <span className="stat__n">{aggregate.suppressed_cells}</span>
                <span className="stat__k">Cells suppressed</span>
              </div>
              <div className="stat">
                <span className="stat__n">{aggregate.min_count}</span>
                <span className="stat__k">Privacy floor</span>
              </div>
            </div>
            <table className="cert">
              <thead>
                <tr>
                  <th scope="col">{groupBy}</th>
                  <th scope="col">Reports</th>
                </tr>
              </thead>
              <tbody>
                {aggregate.groups.map((g) => (
                  <tr key={g.key}>
                    <td>{g.key}</td>
                    <td>{g.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="field__hint">{aggregate.privacy_note}</p>
          </>
        )}
      </section>

      <section style={{ marginTop: 'var(--s7)' }}>
        <h2>What a tamper looks like</h2>
        <p>
          The test suite includes a tampering test: it edits a stored audit entry directly in the
          database and asserts that verification fails and points at the edited row. That is the
          difference between claiming tamper-evidence and demonstrating it. See{' '}
          <span className="mono">backend/tests/test_provenance.py</span>.
        </p>
      </section>
    </>
  )
}
