import { useState } from 'react'
import { api } from '../lib/api.js'

const EXAMPLES = [
  'Materials for Ogun LGA-1 arrived two hours late according to the observer group.',
  'I heard something is wrong with the new voting app.',
  'They said the result sheet for that unit was never uploaded to the portal.',
  'Dem say the BVAS no dey work for that polling unit since morning.',
]

export default function ClaimsPage() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async (text) => {
    const value = (text ?? query).trim()
    if (value.length < 3) {
      setError('Enter at least a few words.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await api.matchClaim({ query: value }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-intro">
        <p className="page-intro__eyebrow">Claim matching</p>
        <h1>Have we already checked something like this?</h1>
        <p className="page-intro__lede">
          Paste a message that is spreading. SHAIDA looks for the closest item already in the
          fact-check archive, so a reviewer does not re-do work. It answers “is this familiar?”,
          never “is this true?”, and it abstains when nothing is close enough.
        </p>
      </div>

      <div className="notice notice--info">
        <h3>Why matching, not classifying</h3>
        <p>
          The official brief for this track forbids tools that label someone's speech as false
          without human review, and warns that classifiers are brittle and easily evaded. Finding
          a near-duplicate of an existing, human-checked item is defensible; issuing a verdict is
          not. Character n-gram matching also survives typos, Pidgin spelling and code-switching,
          which word-level matching does not.
        </p>
      </div>

      <form
        className="card"
        onSubmit={(e) => {
          e.preventDefault()
          run()
        }}
      >
        <div className="field">
          <label className="field__label" htmlFor="claim">
            Message text
          </label>
          <textarea
            id="claim"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            maxLength={2000}
            style={{ minHeight: 90 }}
            placeholder="Paste the claim exactly as it reached you."
          />
        </div>
        <div style={{ display: 'flex', gap: 'var(--s3)', flexWrap: 'wrap', alignItems: 'center' }}>
          <button className="btn btn--signal" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" /> Matching…
              </>
            ) : (
              'Find the closest archived claim'
            )}
          </button>
          <span className="field__hint" style={{ margin: 0 }}>
            Try an example:
          </span>
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={() => {
                setQuery(example)
                run(example)
              }}
            >
              {example.length > 42 ? `${example.slice(0, 42)}…` : example}
            </button>
          ))}
        </div>
      </form>

      {error && (
        <div className="verify-panel verify-panel--bad" role="alert" style={{ marginTop: 'var(--s4)' }}>
          {error}
        </div>
      )}

      {result && (
        <section style={{ marginTop: 'var(--s5)' }}>
          <div
            className={`verify-panel verify-panel--${result.abstained ? 'warn' : 'ok'}`}
            style={{ marginBottom: 'var(--s4)' }}
          >
            <h3>{result.abstained ? 'Abstained — a human must decide' : 'Close matches found'}</h3>
            <p style={{ margin: 0 }}>{result.reason}</p>
          </div>

          <div className="stat-row">
            <div className="stat">
              <span className="stat__n">{result.top_similarity}</span>
              <span className="stat__k">Closest similarity</span>
            </div>
            <div className="stat">
              <span className="stat__n">{result.matches.length}</span>
              <span className="stat__k">Matches above floor</span>
            </div>
            <div className="stat">
              <span className="stat__n">{result.archive_size}</span>
              <span className="stat__k">Claims in archive</span>
            </div>
          </div>

          {result.matches.length > 0 && (
            <table className="cert">
              <thead>
                <tr>
                  <th scope="col">Archived claim</th>
                  <th scope="col">Similarity</th>
                  <th scope="col">Prior reviewer label</th>
                  <th scope="col">Language</th>
                  <th scope="col">Channel</th>
                </tr>
              </thead>
              <tbody>
                {result.matches.map((m) => (
                  <tr key={m.claim_id}>
                    <td className="mono">{m.claim_id}</td>
                    <td>{m.similarity}</td>
                    <td>{m.archived_label}</td>
                    <td>{m.language}</td>
                    <td>{m.channel}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="notice" style={{ marginTop: 'var(--s4)' }}>
            <p style={{ margin: 0 }}>{result.caveat}</p>
          </div>
        </section>
      )}
    </>
  )
}
