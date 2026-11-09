import { useEffect, useState } from 'react'
import { api } from '../lib/api.js'

const HARM_WEIGHTS = [
  ['severity', 0.35, 'How serious the reporter said it was, or the assistive estimate if the reporter did not say.'],
  ['sensitivity', 0.2, 'Whether the category can endanger a person, which changes handling, not the verdict.'],
  ['reach', 0.2, 'How widely a claim is spreading, or how many people reported the same thing.'],
  ['evidence', 0.1, 'Whether an evidence file was attached and hashed.'],
  ['procedural', 0.1, 'Whether the report touches a published procedural rule.'],
  ['freshness', 0.05, 'How recent the report is.'],
]

const LANGUAGES = [
  ['en', 'English'],
  ['pcm', 'Nigerian Pidgin'],
  ['ha', 'Hausa'],
  ['yo', 'Yoruba'],
  ['ig', 'Igbo'],
]

export default function AboutPage() {
  const [stats, setStats] = useState(null)
  const [datasets, setDatasets] = useState(null)

  useEffect(() => {
    Promise.all([api.stats(), api.datasets()])
      .then(([s, d]) => {
        setStats(s)
        setDatasets(d)
      })
      .catch(() => {})
  }, [])

  return (
    <>
      <div className="page-intro">
        <p className="page-intro__eyebrow">About and limits</p>
        <h1>What SHAIDA is, and what it will not do</h1>
        <p className="page-intro__lede">
          SHAIDA is a working prototype built for the Rise Networks #AI4Elections Hackathon 2026.
          It was designed around one rule: a tool may help people check evidence, but it must
          never decide an electoral question for them.
        </p>
      </div>

      <div className="grid grid--2">
        <section className="card">
          <h2>The problem it addresses</h2>
          <p>
            A citizen, observer or fact-checker can capture electoral evidence, but has no
            trustworthy, private, offline-capable way to prove it has not been altered, check it
            against objective public rules, and get it in front of a human reviewer with a clear
            reason — without the tool declaring a result, accusing a person, or exposing the
            reporter.
          </p>
          <p>
            SHAIDA does exactly that, and nothing else. It maps to the official Track 5 brief
            (structured observation, evidence hygiene, triage), Track 2 (deterministic result
            checks for human review) and Track 4 (privacy-preserving reporting, tamper-evident
            audit trails), with multilingual support from Track 3.
          </p>
        </section>

        <section className="card">
          <h2>What it does not do</h2>
          <ul>
            <li>It does not declare results, winners, or fraud. Its outputs are flags.</li>
            <li>It does not accuse or name any individual.</li>
            <li>It does not collect reporter identity — there is no field for it.</li>
            <li>It does not access, scan or test any live electoral system.</li>
            <li>It does not publish precise locations for sensitive reports.</li>
            <li>It does not make automated decisions; every flag needs a human decision.</li>
          </ul>
        </section>
      </div>

      <section style={{ marginTop: 'var(--s6)' }}>
        <h2>How a report is ranked</h2>
        <p>
          Ranking is a transparent weighted sum. Every weight is published here and every
          contribution is shown on each report, so a reviewer can see exactly why something is at
          the top of the queue.
        </p>
        <table className="cert">
          <thead>
            <tr>
              <th scope="col">Signal</th>
              <th scope="col">Weight</th>
              <th scope="col">Meaning</th>
            </tr>
          </thead>
          <tbody>
            {HARM_WEIGHTS.map(([name, weight, meaning]) => (
              <tr key={name}>
                <td className="mono">{name}</td>
                <td>{weight}</td>
                <td>{meaning}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="field__hint">
          The score orders a queue. It is not a judgement about a report's truth, and it is not
          evidence of anything.
        </p>
      </section>

      <section style={{ marginTop: 'var(--s6)' }}>
        <h2>Languages</h2>
        <p>
          The interface and the reviewer explanations are available in all five languages below.
          Explanations are generated from fixed templates filled with the deterministic findings —
          not by a language model — so no sentence about someone's evidence can be invented.
        </p>
        <ul>
          {LANGUAGES.map(([code, name]) => (
            <li key={code}>
              <span className="mono">{code}</span> — {name}
            </li>
          ))}
        </ul>
        <p className="field__hint">
          Hausa, Yoruba and Igbo strings are first-pass translations by the project team and must
          be reviewed by native speakers before any real use. That review has not yet happened,
          and we say so rather than implying otherwise.
        </p>
      </section>

      <section style={{ marginTop: 'var(--s6)' }}>
        <h2>Data and models in use</h2>
        {datasets && (
          <p>
            Official synthetic starter pack loaded: {datasets.loaded?.join(', ') || 'none'}
            {datasets.missing?.length ? ` (missing: ${datasets.missing.join(', ')})` : ''}.
          </p>
        )}
        {stats && (
          <table className="cert">
            <tbody>
              <tr>
                <td>Reports held</td>
                <td>{stats.reports}</td>
              </tr>
              <tr>
                <td>Audit entries</td>
                <td>{stats.audit_entries}</td>
              </tr>
              <tr>
                <td>Archive claims</td>
                <td>{stats.archive_claims}</td>
              </tr>
              <tr>
                <td>Severity assist available</td>
                <td>{String(stats.severity_assist_available)}</td>
              </tr>
              <tr>
                <td>Result records</td>
                <td>{stats.result_records}</td>
              </tr>
            </tbody>
          </table>
        )}
        <p className="field__hint">
          All data is synthetic or public. No personal data, no live-system data, and no
          scraped content is used anywhere in this prototype.
        </p>
      </section>

      <section style={{ marginTop: 'var(--s6)' }}>
        <h2>Conditions before any real use</h2>
        <ul>
          <li>Independent security review of the API and the hash chain.</li>
          <li>Native-speaker review of every non-English string.</li>
          <li>An accessibility audit with assistive-technology users.</li>
          <li>An ethics and data-protection review under the Nigeria Data Protection Act 2023.</li>
          <li>Written agreements with any CSO that would operate it.</li>
          <li>A pilot in a controlled sandbox, with no connection to production systems.</li>
        </ul>
        <p>
          <strong>
            This prototype is not approved for operational electoral deployment.
          </strong>{' '}
          Winning a competition would not change that.
        </p>
      </section>
    </>
  )
}
