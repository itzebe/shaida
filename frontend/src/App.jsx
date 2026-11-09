import { useEffect, useState } from 'react'
import { api } from './lib/api.js'
import ReportPage from './pages/ReportPage.jsx'
import QueuePage from './pages/QueuePage.jsx'
import ResultsPage from './pages/ResultsPage.jsx'
import ClaimsPage from './pages/ClaimsPage.jsx'
import IntegrityPage from './pages/IntegrityPage.jsx'
import AboutPage from './pages/AboutPage.jsx'

const TABS = [
  { id: 'report', label: 'File a report', Component: ReportPage },
  { id: 'queue', label: 'Reviewer queue', Component: QueuePage },
  { id: 'results', label: 'Result checks', Component: ResultsPage },
  { id: 'claims', label: 'Claim matching', Component: ClaimsPage },
  { id: 'integrity', label: 'Integrity', Component: IntegrityPage },
  { id: 'about', label: 'About and limits', Component: AboutPage },
]

export default function App() {
  const [tab, setTab] = useState('report')
  const [online, setOnline] = useState(true)
  const [health, setHealth] = useState(null)

  // Register the service worker so the app shell survives a lost connection.
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {})
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      try {
        const result = await api.health()
        if (!cancelled) {
          setOnline(true)
          setHealth(result)
        }
      } catch {
        if (!cancelled) setOnline(false)
      }
    }
    check()
    const timer = setInterval(check, 15000)
    const onOnline = () => setOnline(true)
    const onOffline = () => setOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      cancelled = true
      clearInterval(timer)
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const Active = TABS.find((t) => t.id === tab)?.Component ?? ReportPage

  return (
    <div className="app">
      <a className="skip-link" href="#main">
        Skip to main content
      </a>

      {!online && (
        <div className="offline-banner" role="status">
          Offline. Your draft is kept on this device and sent when the service returns.
        </div>
      )}

      <header className="masthead">
        <div className="masthead__inner">
          <a className="brand" href="#main">
            <span className="brand__mark">SHAIDA</span>
            <span className="brand__tag">Verifiable electoral evidence</span>
          </a>
          <span className="masthead__claim">
            {health ? `v${health.version} · flags only · no verdicts` : 'connecting…'}
          </span>
        </div>
      </header>

      <nav className="nav" aria-label="Sections">
        <div className="nav__inner" role="tablist">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              role="tab"
              id={`tab-${id}`}
              aria-selected={tab === id}
              aria-controls={`panel-${id}`}
              tabIndex={tab === id ? 0 : -1}
              className="nav__tab"
              onClick={() => setTab(id)}
              onKeyDown={(event) => {
                const index = TABS.findIndex((t) => t.id === tab)
                if (event.key === 'ArrowRight') {
                  event.preventDefault()
                  setTab(TABS[(index + 1) % TABS.length].id)
                } else if (event.key === 'ArrowLeft') {
                  event.preventDefault()
                  setTab(TABS[(index - 1 + TABS.length) % TABS.length].id)
                } else if (event.key === 'Home') {
                  event.preventDefault()
                  setTab(TABS[0].id)
                } else if (event.key === 'End') {
                  event.preventDefault()
                  setTab(TABS[TABS.length - 1].id)
                }
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="main" id="main" tabIndex={-1}>
        <div id={`panel-${tab}`} role="tabpanel" aria-labelledby={`tab-${tab}`}>
          <Active online={online} />
        </div>
      </main>

      <footer className="colophon">
        <div className="colophon__inner">
          <div>
            <strong>SHAIDA</strong> is a working prototype built for the Rise Networks
            #AI4Elections Hackathon 2026. It is <strong>not approved for operational
            deployment</strong> and does not access any live electoral system.
          </div>
          <div>
            Synthetic and public data only. No reporter identity is collected. Every automated
            output is a flag for human review.
          </div>
        </div>
      </footer>
    </div>
  )
}
