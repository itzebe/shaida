// Shared UI vocabulary and small helpers.

export const BAND_LABEL = {
  urgent: 'Urgent',
  high: 'High',
  medium: 'Medium',
  routine: 'Routine',
}

export const DECISION_LABEL = {
  accepted: 'Accepted for follow-up',
  needs_more_evidence: 'Needs more evidence',
  referred_to_cso: 'Referred to a CSO',
  not_pursued: 'Not pursued',
  duplicate: 'Duplicate of an earlier report',
}

export const CATEGORY_LABEL = {
  logistics_delay: 'Logistics delay',
  positive_practice: 'Positive practice',
  intimidation: 'Intimidation',
  accessibility_barrier: 'Accessibility barrier',
  information_gap: 'Information gap',
  equipment_failure: 'Equipment failure',
  queue_management: 'Queue management',
  result_sheet_issue: 'Result-sheet issue',
  result_upload_delay: 'Result-upload delay',
  bvas_malfunction: 'BVAS malfunction',
  misinformation_claim: 'Misinformation claim',
  voter_intimidation: 'Voter intimidation',
  violence_or_threat: 'Violence or threat',
  staffing_shortfall: 'Staffing shortfall',
  procedural_irregularity: 'Procedural irregularity',
  other: 'Other',
}

export const SEVERITY_LABEL = ['Informational', 'Minor', 'Moderate', 'Serious', 'Critical']

export function titleCase(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function shortHash(hash, head = 10, tail = 6) {
  if (!hash || hash.length < head + tail + 1) return hash || '—'
  return `${hash.slice(0, head)}…${hash.slice(-tail)}`
}

export function formatTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

// SHA-256 in the browser, used to hash evidence before it ever leaves the device.
// This is what lets a reporter prove what they submitted without trusting the server.
export async function sha256HexFromBase64(b64) {
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i)
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

export function SeverityBar({ value }) {
  const level = Math.max(0, Math.min(4, Number(value) || 0))
  return (
    <span
      className="sevbar"
      role="img"
      aria-label={`Reported severity ${level} of 4, ${SEVERITY_LABEL[level]}`}
    >
      {[0, 1, 2, 3, 4].map((i) => (
        <span key={i} className={`sevbar__pip ${i <= level ? 'sevbar__pip--on' : ''}`} />
      ))}
    </span>
  )
}

export function BandBadge({ band }) {
  return <span className={`badge badge--${band || 'routine'}`}>{BAND_LABEL[band] || band}</span>
}
