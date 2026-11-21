import { useEffect, useRef, useState } from 'react'
import { ENGINES, VoiceClient } from './voice.js'
import { Customers, Ledger, Orders, Settings } from './screens.jsx'
import { ErrorBoundary } from './ErrorBoundary.jsx'
import { Icon } from './Icon.jsx'
import { VoiceConsole } from './VoiceConsole.jsx'
import { ActionSheet, Greeting, QuickActions, RecentEntries, Summary, TopDues, Week, useDashboard } from './Dashboard.jsx'

export const LANG_NAMES = { auto: 'Auto', en: 'English', hi: 'हिन्दी', kn: 'ಕನ್ನಡ', te: 'తెలుగు', ta: 'தமிழ்' }
const ENGINE_NAMES = { live: 'Gnani Live', rest: 'Gnani REST', browser: 'Browser speech' }
const TABS = [['home', 'home'], ['customers', 'users'], ['orders', 'box'], ['ledger', 'book'], ['settings', 'cog']]
export const api = (path, opts) =>
  fetch(path, opts).then((r) => (r.ok ? r.json() : r.json().catch(() => ({})).then((e) => Promise.reject(new Error(e.detail || r.status)))))

const store = { // per-device conveniences only; the app works without storage
  get: (k) => { try { return localStorage.getItem(k) } catch { return null } },
  set: (k, v) => { try { localStorage.setItem(k, v) } catch { /* blocked */ } },
}

export default function App() {
  const [meta, setMeta] = useState(null)
  const [settings, setSettings] = useState(null)
  const [tab, setTab] = useState('home')
  const [lang, setLang] = useState(store.get('bk_lang') || 'auto')
  const [uiLang, setUiLang] = useState(() => { const l = store.get('bk_lang'); return l && l !== 'auto' ? l : 'en' })
  const [engine, setEngine] = useState('live')
  const [bargeIn, setBargeIn] = useState(false)
  const [brainOn, setBrainOn] = useState(true)
  const [started, setStarted] = useState(false)
  const [openCustomer, setOpenCustomer] = useState(null)
  const [reminders, setReminders] = useState(null)
  const [showReminders, setShowReminders] = useState(false)
  const [sheet, setSheet] = useState(null)
  const [version, setVersion] = useState(0)
  const [micSettings, setMicSettings] = useState(null)
  const voice = useRef(null)
  const consoleRef = useRef(null)
  const [conv, setConv] = useState({ transcript: '', reply: null, latency: {}, notice: '', listening: false, speaking: false })
  const dash = useDashboard(version)

  useEffect(() => {
    Promise.all([api('/api/meta'), api('/api/settings')]).then(([m, s]) => {
      setMeta(m)
      setSettings(s)
      if (!store.get('bk_lang') && s.default_language && s.default_language !== 'auto') {
        setLang(s.default_language)
        setUiLang(s.default_language)
      }
    }).catch(() => setMeta({ ui: null, failed: true }))
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {})
  }, [])
  const uiLangRef = useRef(uiLang)
  uiLangRef.current = uiLang

  // Reminders (customers without phone numbers, pending orders) — always behind the bell; once a day after closing
  // time the panel also opens by itself and the summary is spoken.
  useEffect(() => {
    if (!meta?.ui) return
    const check = async () => {
      try {
        const e = await api(`/api/evening?lang=${uiLangRef.current}`)
        setReminders(e)
        const today = new Date().toISOString().slice(0, 10)
        const s = await api('/api/settings')
        const now = new Date()
        const hhmm = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
        if (store.get('bk_evening') !== today && hhmm >= s.closing_time && (e.missing.length || e.orders.length)) {
          setShowReminders(true)
          voice.current?.sendJson({ type: 'evening' })
          store.set('bk_evening', today)
        }
      } catch { /* offline: try again next minute */ }
    }
    check()
    const id = setInterval(check, 60000)
    return () => clearInterval(id)
  }, [meta, started, version])

  const t = (k) => meta?.ui?.[uiLang]?.[k] ?? meta?.ui?.en?.[k] ?? k
  const patch = (p) => setConv((c) => ({ ...c, ...p }))

  function onEvent(m) {
    switch (m.type) {
      case 'transcript':
        // new request: clear the previous reply so it can't be mistaken for this one
        setConv((c) => ({ ...c, transcript: m.text, reply: null, thinking: true, failed: false, latency: { stt: m.stt_ms } }))
        break
      case 'ignored':
        patch({ thinking: false })
        break
      case 'error':
        patch({ thinking: false, failed: true }) // this request failed; the app stays usable
        break
      case 'disconnected':
        setConv((c) => ({ ...c, listening: false, speaking: false, offline: true }))
        break
      case 'connected':
        patch({ offline: false })
        break
      case 'reply':
        setUiLang(m.lang)
        if (!m.evening) patch({ reply: m, notice: '', thinking: false, failed: false })
        if (m.source) setConv((c) => ({ ...c, latency: { ...c.latency, source: m.source, brain: m.brain_ms } }))
        if (m.saved || m.key === 'undone') setVersion((v) => v + 1) // the dashboard follows the ledger live
        break
      case 'latency':
        setConv((c) => ({ ...c, latency: { ...c.latency, reply: m.reply } }))
        break
      case 'speaking':
        patch({ speaking: m.value })
        break
      case 'engine_failed':
        if (m.next) {
          setEngine(m.next)
          patch({ notice: `${t('engineFallback')} ${ENGINE_NAMES[m.next]}` })
        }
        break
      case 'warning':
        patch({ notice: m.key ? t(m.key) : `Gnani: ${m.detail}` })
        break
      case 'nomic':
        patch({ notice: m.reason === 'missing' ? t('micMissing') : t('micDenied'), listening: false })
        break
      case 'micSettings':
        setMicSettings(m.settings)
        break
      case 'playbackFailed':
        patch({ notice: t('playbackFailed'), speaking: false })
        break
    }
  }
  const onEventRef = useRef(onEvent)
  onEventRef.current = onEvent

  function ensureStarted() {
    if (voice.current) return voice.current
    voice.current = new VoiceClient((m) => onEventRef.current(m), { engine, lang, bargeIn })
    voice.current.connect()
    setStarted(true)
    return voice.current
  }

  useEffect(() => {
    if (!conv.thinking) return
    const id = setTimeout(() => patch({ thinking: false, failed: true }), 15000) // no reply in 15 s: let the user retry
    return () => clearTimeout(id)
  }, [conv.thinking, conv.transcript])

  function submit(said) {
    const v = ensureStarted()
    patch({ transcript: said, reply: null, thinking: true, failed: false, lastSaid: said })
    v.sendText(said)
  }

  async function toggleMic() {
    const v = ensureStarted()
    if (conv.listening) {
      patch({ listening: false })
      await v.micStop()
    } else if (await v.micStart()) {
      patch({ listening: true, notice: '' })
    }
  }

  function micFromAnywhere() {
    setTab('home')
    if (!conv.listening) toggleMic()
  }

  async function cycleEngine() {
    const next = ENGINES[(ENGINES.indexOf(engine) + 1) % ENGINES.length]
    if (conv.listening) {
      await voice.current.micStop()
      patch({ listening: false })
    }
    setEngine(next)
    voice.current?.setConfig({ engine: next })
  }

  function changeLang(l) {
    setLang(l)
    store.set('bk_lang', l)
    setUiLang(l === 'auto' ? (conv.reply?.lang || 'en') : l)
    voice.current?.setConfig({ lang: l })
  }

  function openCustomerPage(id) {
    setOpenCustomer(id)
    setTab('customers')
  }

  if (!meta) return <div className="splash">BolKhata</div>
  if (meta.failed) {
    return (
      <div className="splash"><p>Can't reach the BolKhata server. Check that it is running, then try again.</p>
        <button className="btn solid" onClick={() => location.reload()}>Try again</button></div>
    )
  }

  const pendingOrders = dash.data?.orders.filter((o) => o.status === 'pending').length || 0
  const bellCount = reminders ? reminders.missing.length + reminders.orders.length : 0
  const langSelect = (
    <select className="lang-select" aria-label={t('language')} value={lang} onChange={(e) => changeLang(e.target.value)}>
      {Object.entries(LANG_NAMES).map(([k, v]) => <option key={k} value={k}>{k === 'auto' ? `${t('auto')}` : v}</option>)}
    </select>
  )
  const consoleEl = (
    <div ref={consoleRef}>
      <VoiceConsole t={t} conv={conv} voice={voice.current} started={started} onStart={() => ensureStarted()} onMic={toggleMic}
        onSubmit={submit} lang={lang} uiLang={uiLang} engine={engine} onEngine={cycleEngine}
        bargeIn={bargeIn} onBarge={() => { setBargeIn(!bargeIn); voice.current?.setConfig({ bargeIn: !bargeIn }) }}
        brainOn={brainOn} onBrain={() => { setBrainOn(!brainOn); voice.current?.setConfig({ brain: !brainOn }) }}
        llm={meta.llm && meta.llm.length > 0} />
    </div>
  )

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark" aria-hidden="true">ब</span><div><b>BolKhata</b><small>{settings?.shop_name}</small></div></div>
        <nav className="side-nav" aria-label="Main">
          {TABS.map(([k, icon]) => (
            <button key={k} className={tab === k ? 'is-active' : ''} aria-current={tab === k ? 'page' : undefined} onClick={() => setTab(k)}>
              <Icon name={icon} />{t(k)}{k === 'orders' && pendingOrders > 0 && <span className="count">{pendingOrders}</span>}
            </button>
          ))}
        </nav>
        <div className="side-foot">{langSelect}</div>
      </aside>

      <div className="main-col">
        <header className="topbar">
          <div className="brand compact"><span className="brand-mark" aria-hidden="true">ब</span><div><b>BolKhata</b><small>{settings?.shop_name}</small></div></div>
          <span className={`conn ${conv.offline ? 'is-off' : ''}`} title={conv.offline ? t('offline') : t('online')}>
            <i />{conv.offline ? '' : t('online')}
          </span>
          <button className="icon-btn" onClick={() => setShowReminders(!showReminders)} aria-label={`${t('notifications')} (${bellCount})`}
            aria-expanded={showReminders}>
            <Icon name="bell" />{bellCount > 0 && <span className="badge">{bellCount}</span>}
          </button>
          <div className="topbar-lang">{langSelect}</div>
        </header>

        <main className={`page-${tab}`}>
          {showReminders && reminders && (
            <section className="reminders" role="status">
              <header className="panel-head"><h2>{t('notifications')}</h2>
                <button className="link" onClick={() => setShowReminders(false)}>{t('dismiss')}</button></header>
              {bellCount === 0 ? <p className="empty">{t('allClear')}</p> : (
                <>
                  <p>{reminders.text}</p>
                  <div className="choices">
                    {reminders.missing.map((c) => (
                      <button key={c.id} className="choice" onClick={() => openCustomerPage(c.id)}>
                        <Icon name="phone" size={16} /> {c.name}{c.note && `, ${c.note}`}
                      </button>
                    ))}
                    {reminders.orders.length > 0 && <button className="choice" onClick={() => setTab('orders')}><Icon name="box" size={16} /> {t('orders')}</button>}
                  </div>
                </>
              )}
            </section>
          )}

          <ErrorBoundary key={tab} message={t('failed')} retry={t('retry')}>
            {tab === 'home' && (
              <div className="home">
                <Greeting t={t} shop={settings?.shop_name} />
                {dash.err && <p className="notice" role="alert">{t('failed')} <button className="link" onClick={dash.reload}>{t('retry')}</button></p>}
                {dash.data && <Summary t={t} data={dash.data} />}
                <div className="home-grid">
                  <div className="home-voice">{consoleEl}
                    <QuickActions t={t} onAction={setSheet} onLedger={() => setTab('ledger')} />
                  </div>
                  {dash.data && (
                    <div className="home-info">
                      <RecentEntries t={t} data={dash.data} onSeeAll={() => setTab('ledger')} />
                      <TopDues t={t} data={dash.data} onOpen={openCustomerPage} />
                      <Week t={t} data={dash.data} pendingOrders={pendingOrders} onOrders={() => setTab('orders')} />
                    </div>
                  )}
                </div>
              </div>
            )}
            {tab === 'customers' && <Customers t={t} uiLang={uiLang} open={openCustomer} setOpen={setOpenCustomer} />}
            {tab === 'orders' && <Orders t={t} uiLang={uiLang} />}
            {tab === 'ledger' && <Ledger t={t} />}
            {tab === 'settings' && <Settings t={t} meta={meta} micSettings={micSettings} onSaved={(s) => { setSettings(s); setVersion((v) => v + 1) }} />}
          </ErrorBoundary>
        </main>
      </div>

      {tab !== 'home' && (
        <button className={`fab-mic ${conv.listening ? 'is-live' : ''}`} onClick={micFromAnywhere} aria-label={t('tapToSpeak')}>
          <Icon name="mic" size={24} />
        </button>
      )}

      <nav className="bottom-nav" aria-label="Main">
        {TABS.map(([k, icon]) => (
          <button key={k} className={tab === k ? 'is-active' : ''} aria-current={tab === k ? 'page' : undefined} onClick={() => setTab(k)}>
            <Icon name={icon} size={22} /><span>{t(k)}</span>
            {k === 'orders' && pendingOrders > 0 && <span className="badge">{pendingOrders}</span>}
          </button>
        ))}
      </nav>

      {sheet && dash.data && (
        <ActionSheet t={t} kind={sheet} uiLang={uiLang} customers={dash.data.customers} onClose={() => setSheet(null)}
          onSend={(cmd) => { setSheet(null); setTab('home'); submit(cmd); consoleRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' }) }} />
      )}
    </div>
  )
}
