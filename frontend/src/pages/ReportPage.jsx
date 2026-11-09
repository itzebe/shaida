import { useEffect, useMemo, useRef, useState } from 'react'
import { api, ApiError } from '../lib/api.js'
import { CATEGORY_LABEL, sha256HexFromBase64, shortHash, titleCase } from '../lib/ui.jsx'

const DRAFT_KEY = 'shaida.draft.v1'
const OUTBOX_KEY = 'shaida.outbox.v1'

const CATEGORIES = Object.keys(CATEGORY_LABEL)
const REPORTER_TYPES = ['citizen', 'observer', 'party_agent', 'official']

function loadDraft() {
  try {
    return JSON.parse(localStorage.getItem(DRAFT_KEY) || '{}')
  } catch {
    return {}
  }
}

export default function ReportPage({ online = true }) {
  const [form, setForm] = useState(() => ({
    category: 'logistics_delay',
    narrative: '',
    state_name: '',
    lga: '',
    ward: '',
    pu_id: '',
    reporter_type: 'citizen',
    evidence_kind: 'text_only',
    severity_reported: '',
    latitude: '',
    longitude: '',
    ...loadDraft(),
  }))
  const [evidence, setEvidence] = useState(null) // { name, b64, sha }
  const [evidenceBusy, setEvidenceBusy] = useState(false)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [serverError, setServerError] = useState('')
  const [outbox, setOutbox] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(OUTBOX_KEY) || '[]')
    } catch {
      return []
    }
  })
  const [localHash, setLocalHash] = useState('')
  const fileRef = useRef(null)

  // Persist the draft on every change: a lost connection must never lose a citizen's report.
  useEffect(() => {
    const { ...persistable } = form
    localStorage.setItem(DRAFT_KEY, JSON.stringify(persistable))
  }, [form])

  // Compute the local content hash as the reporter types, so they can see the commitment
  // before anything is sent.
  useEffect(() => {
    let cancelled = false
    const payload = JSON.stringify({
      category: form.category,
      narrative: form.narrative.trim(),
      state: form.state_name.trim(),
      pu_id: form.pu_id.trim() || null,
      severity_reported: form.severity_reported === '' ? null : Number(form.severity_reported),
    })
    crypto.subtle
      .digest('SHA-256', new TextEncoder().encode(payload))
      .then((digest) => {
        if (cancelled) return
        setLocalHash([...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join(''))
      })
      .catch(() => setLocalHash(''))
    return () => {
      cancelled = true
    }
  }, [form.category, form.narrative, form.state_name, form.pu_id, form.severity_reported])

  const update = (key) => (event) => setForm((f) => ({ ...f, [key]: event.target.value }))

  const onEvidence = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      setEvidence(null)
      return
    }
    if (file.size > 5_000_000) {
      setErrors((e) => ({ ...e, evidence: 'Evidence must be 5 MB or smaller.' }))
      return
    }
    setEvidenceBusy(true)
    try {
      const buffer = await file.arrayBuffer()
      const bytes = new Uint8Array(buffer)
      let binary = ''
      for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i])
      const b64 = btoa(binary)
      const sha = await sha256HexFromBase64(b64)
      setEvidence({ name: file.name, b64, sha, size: file.size })
      setErrors((e) => ({ ...e, evidence: undefined }))
    } catch {
      setErrors((e) => ({ ...e, evidence: 'Could not read that file.' }))
    } finally {
      setEvidenceBusy(false)
    }
  }

  const buildPayload = () => {
    const payload = {
      category: form.category,
      narrative: form.narrative.trim(),
      state_name: form.state_name.trim(),
      lga: form.lga.trim() || null,
      ward: form.ward.trim() || null,
      pu_id: form.pu_id.trim() || null,
      reporter_type: form.reporter_type,
      channel: 'pwa',
      evidence_kind: evidence ? 'photo' : 'text_only',
      severity_reported: form.severity_reported === '' ? null : Number(form.severity_reported),
    }
    if (evidence) {
      payload.evidence_b64 = evidence.b64
      payload.evidence_sha256 = evidence.sha
    }
    // Coordinates are optional and deliberately coarse; the server rounds them further.
    if (form.latitude !== '' && form.longitude !== '') {
      payload.latitude = Number(form.latitude)
      payload.longitude = Number(form.longitude)
    }
    return payload
  }

  const validate = () => {
    const next = {}
    if (form.narrative.trim().length < 10) next.narrative = 'Please describe what you saw in at least 10 characters.'
    if (form.state_name.trim().length < 2) next.state_name = 'State is required.'
    if (form.latitude !== '' && form.longitude === '') next.longitude = 'Longitude is required if you give latitude.'
    if (form.longitude !== '' && form.latitude === '') next.latitude = 'Latitude is required if you give longitude.'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const queueOffline = (payload) => {
    const next = [...outbox, { queuedAt: new Date().toISOString(), payload }]
    setOutbox(next)
    localStorage.setItem(OUTBOX_KEY, JSON.stringify(next))
  }

  const flushOutbox = async () => {
    if (outbox.length === 0) return
    const remaining = []
    let sent = 0
    for (const item of outbox) {
      try {
        await api.createReport(item.payload)
        sent += 1
      } catch (error) {
        if (error instanceof ApiError && error.code === 'offline') remaining.push(item)
        else sent += 1 // a rejected item is not retryable; drop it and report below
      }
    }
    setOutbox(remaining)
    localStorage.setItem(OUTBOX_KEY, JSON.stringify(remaining))
    if (sent > 0) setResult((r) => ({ ...(r || {}), flushed: sent }))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setServerError('')
    setResult(null)
    if (!validate()) return
    setSubmitting(true)
    const payload = buildPayload()
    try {
      const created = await api.createReport(payload)
      setResult(created)
      localStorage.removeItem(DRAFT_KEY)
      setForm((f) => ({ ...f, narrative: '', pu_id: '' }))
      setEvidence(null)
      if (fileRef.current) fileRef.current.value = ''
      if (outbox.length) await flushOutbox()
    } catch (error) {
      if (error instanceof ApiError && error.code === 'offline') {
        queueOffline(payload)
        setResult({ queued: true, content_hash: localHash })
      } else {
        setServerError(error.message)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const severityOptions = useMemo(
    () => [
      { value: '', label: 'Not sure / leave it to the reviewer' },
      { value: '0', label: '0 — Informational' },
      { value: '1', label: '1 — Minor' },
      { value: '2', label: '2 — Moderate' },
      { value: '3', label: '3 — Serious' },
      { value: '4', label: '4 — Critical' },
    ],
    [],
  )

  return (
    <div className="grid grid--2">
      <section>
        <div className="page-intro">
          <p className="page-intro__eyebrow">File a report</p>
          <h1>Record what happened, so it cannot be changed later</h1>
          <p className="page-intro__lede">
            SHAIDA hashes your report on this device and adds it to a tamper-evident log. It
            will be queued for a human reviewer. It will never accuse anyone, and it will never
            publish your identity — none is collected.
          </p>
        </div>

        <form className="card" onSubmit={onSubmit} noValidate>
          <div className="field">
            <label className="field__label" htmlFor="category">
              What kind of issue is this?
            </label>
            <select id="category" value={form.category} onChange={update('category')}>
              {CATEGORIES.map((key) => (
                <option key={key} value={key}>
                  {CATEGORY_LABEL[key]}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label className="field__label" htmlFor="narrative">
              Describe what you observed
            </label>
            <textarea
              id="narrative"
              value={form.narrative}
              onChange={update('narrative')}
              maxLength={2000}
              aria-describedby="narrative-hint"
              aria-invalid={Boolean(errors.narrative)}
              placeholder="For example: materials had not arrived at the unit by 9am, and about 200 people were waiting with no shade."
            />
            <span className="field__hint" id="narrative-hint">
              {form.narrative.length}/2000 characters. Write only what you personally saw or
              were told. Do not name private individuals.
            </span>
            {errors.narrative && <span className="field__error">{errors.narrative}</span>}
          </div>

          <div className="grid grid--2">
            <div className="field">
              <label className="field__label" htmlFor="state_name">
                State
              </label>
              <input
                id="state_name"
                type="text"
                value={form.state_name}
                onChange={update('state_name')}
                aria-invalid={Boolean(errors.state_name)}
                autoComplete="address-level1"
              />
              {errors.state_name && <span className="field__error">{errors.state_name}</span>}
            </div>
            <div className="field">
              <label className="field__label" htmlFor="lga">
                LGA (optional)
              </label>
              <input id="lga" type="text" value={form.lga} onChange={update('lga')} />
            </div>
          </div>

          <div className="grid grid--2">
            <div className="field">
              <label className="field__label" htmlFor="ward">
                Ward (optional)
              </label>
              <input id="ward" type="text" value={form.ward} onChange={update('ward')} />
            </div>
            <div className="field">
              <label className="field__label" htmlFor="pu_id">
                Polling-unit code (optional)
              </label>
              <input id="pu_id" type="text" value={form.pu_id} onChange={update('pu_id')} placeholder="SIM-00001" />
            </div>
          </div>

          <div className="grid grid--2">
            <div className="field">
              <label className="field__label" htmlFor="reporter_type">
                Who is reporting?
              </label>
              <select id="reporter_type" value={form.reporter_type} onChange={update('reporter_type')}>
                {REPORTER_TYPES.map((key) => (
                  <option key={key} value={key}>
                    {titleCase(key)}
                  </option>
                ))}
              </select>
              <span className="field__hint">
                This is a role, not an identity. No name, phone number or account is stored.
              </span>
            </div>
            <div className="field">
              <label className="field__label" htmlFor="severity_reported">
                How serious did it seem?
              </label>
              <select id="severity_reported" value={form.severity_reported} onChange={update('severity_reported')}>
                {severityOptions.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <fieldset className="field" style={{ border: 0, padding: 0, margin: 0 }}>
            <legend className="field__label">Evidence (optional)</legend>
            <input
              ref={fileRef}
              id="evidence"
              type="file"
              accept="image/*,application/pdf,audio/*,video/*"
              onChange={onEvidence}
              aria-describedby="evidence-hint"
            />
            {/* A file input has no accessible name of its own. The legend names the group but
                not the control, so axe reports a missing label. This supplies one without
                duplicating the visible legend. */}
            <label className="visually-hidden" htmlFor="evidence">
              Choose an evidence file to hash
            </label>
            <span className="field__hint" id="evidence-hint">
              A photo or scan. It is hashed on this device before upload, so you can prove later
              exactly what you submitted.
            </span>
            {evidenceBusy && (
              <span className="field__hint">
                <span className="spinner" aria-hidden="true" /> hashing…
              </span>
            )}
            {evidence && (
              <div className="verify-panel verify-panel--ok" style={{ marginTop: 'var(--s3)' }}>
                <strong>Evidence hashed on this device</strong>
                <span className="hashline" style={{ marginTop: 'var(--s2)' }}>
                  sha256:{evidence.sha}
                </span>
              </div>
            )}
            {errors.evidence && <span className="field__error">{errors.evidence}</span>}
          </fieldset>

          <details className="disclosure">
            <summary>Optional: precise location (off by default)</summary>
            <p className="field__hint" style={{ marginTop: 'var(--s3)' }}>
              SHAIDA rounds any coordinates to about one kilometre and never publishes them. For
              reports involving intimidation or violence, consider leaving this blank.
            </p>
            <div className="grid grid--2">
              <div className="field">
                <label className="field__label" htmlFor="latitude">
                  Latitude
                </label>
                <input id="latitude" type="text" inputMode="decimal" value={form.latitude} onChange={update('latitude')} />
              </div>
              <div className="field">
                <label className="field__label" htmlFor="longitude">
                  Longitude
                </label>
                <input id="longitude" type="text" inputMode="decimal" value={form.longitude} onChange={update('longitude')} />
              </div>
            </div>
          </details>

          {localHash && (
            <p className="field__hint" style={{ marginBottom: 'var(--s4)' }}>
              Draft commitment (sha256 of your current text):{' '}
              <span className="mono">{shortHash(localHash, 12, 8)}</span>
            </p>
          )}

          {serverError && (
            <div className="verify-panel verify-panel--bad" role="alert" style={{ marginBottom: 'var(--s4)' }}>
              <strong>Could not submit</strong>
              <p style={{ margin: 0 }}>{serverError}</p>
            </div>
          )}

          <div style={{ display: 'flex', gap: 'var(--s3)', flexWrap: 'wrap' }}>
            <button className="btn btn--signal" type="submit" disabled={submitting || !online}>
              {submitting ? (
                <>
                  <span className="spinner" aria-hidden="true" /> Recording…
                </>
              ) : (
                'Record and hash this report'
              )}
            </button>
            <button
              className="btn btn--ghost"
              type="button"
              onClick={() => {
                setForm({
                  category: 'logistics_delay',
                  narrative: '',
                  state_name: '',
                  lga: '',
                  ward: '',
                  pu_id: '',
                  reporter_type: 'citizen',
                  evidence_kind: 'text_only',
                  severity_reported: '',
                  latitude: '',
                  longitude: '',
                })
                setEvidence(null)
                setErrors({})
                localStorage.removeItem(DRAFT_KEY)
              }}
            >
              Clear draft
            </button>
          </div>
          {!online && (
            <p className="field__hint" style={{ marginTop: 'var(--s3)' }}>
              You are offline. Submitting now will queue the report on this device
              {outbox.length > 0 ? ` (${outbox.length} already queued)` : ''}.
            </p>
          )}
        </form>
      </section>

      <section>
        {result && (
          <div className="verify-panel verify-panel--ok" role="status" style={{ marginBottom: 'var(--s5)' }}>
            <h3>{result.queued ? 'Queued on this device' : 'Recorded'}</h3>
            <p style={{ marginBottom: 'var(--s2)' }}>
              {result.queued
                ? 'SHAIDA is unreachable, so the report is held locally and will be sent when the service returns.'
                : result.message}
            </p>
            {result.id && (
              <>
                <p style={{ margin: 0 }}>
                  Reference: <span className="mono">{result.id}</span>
                </p>
                <p style={{ margin: 0 }}>
                  Priority band: <span className="mono">{result.priority_band}</span> ({result.priority})
                </p>
                <span className="hashline" style={{ marginTop: 'var(--s3)' }}>
                  content sha256: {result.content_hash}
                </span>
                <p className="field__hint" style={{ marginTop: 'var(--s3)' }}>
                  Keep this reference and hash. They are how you, or anyone, can later prove this
                  record was not altered.
                </p>
              </>
            )}
            {result.flushed ? (
              <p style={{ marginBottom: 0 }}>{result.flushed} queued report(s) were sent.</p>
            ) : null}
          </div>
        )}

        <div className="notice notice--info">
          <h3>What SHAIDA does not do</h3>
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            <li>It does not decide whether anything is true, fraudulent or improper.</li>
            <li>It does not collect your name, phone number or account.</li>
            <li>It does not contact the police, INEC or any authority on its own.</li>
            <li>It does not publish unverified reports or name individuals.</li>
          </ul>
        </div>

        <div className="notice">
          <h3>How your report is handled</h3>
          <ol style={{ margin: 0, paddingLeft: '1.1rem' }}>
            <li>Your text is hashed on this device.</li>
            <li>The service stores it with no identity and links it into an append-only log.</li>
            <li>A transparent scoring model orders it against other reports for a human reviewer.</li>
            <li>A named reviewer records a decision and a reason; that too is logged.</li>
          </ol>
        </div>
      </section>
    </div>
  )
}
