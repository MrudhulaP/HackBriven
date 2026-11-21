import { useEffect, useRef, useState } from 'react'
import { ENGINES, VoiceClient } from './voice.js'
import { Customers, Ledger, Orders, Settings } from './screens.jsx'

export const LANG_NAMES = { auto: 'Auto', hi: 'हिन्दी', en: 'English', kn: 'ಕನ್ನಡ', te: 'తెలుగు', ta: 'தமிழ்' }
const ENGINE_NAMES = { live: 'Gnani Live', rest: 'Gnani REST', browser: 'Browser' }
const ENGINE_SHORT = { live: 'Live', rest: 'REST', browser: 'Web' } // fits a phone-width app bar
export const api = (path, opts) =>
  fetch(path, opts).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(new Error(e.detail || r.status)))))

export default function App() {
  const [meta, setMeta] = useState(null)
  const [tab, setTab] = useState('home')
  const [lang, setLang] = useState('auto')
  const [uiLang, setUiLang] = useState('hi')
  const [engine, setEngine] = useState('live')
  const [bargeIn, setBargeIn] = useState(false)
  const [brainOn, setBrainOn] = useState(true)
  const [started, setStarted] = useState(false)
  const [openCustomer, setOpenCustomer] = useState(null)
  const [evening, setEvening] = useState(null)
  const voice = useRef(null)
  const [conv, setConv] = useState({ transcript: '', reply: null, latency: {}, notice: '', listening: false, speaking: false })

  useEffect(() => {
    Promise.all([api('/api/meta'), api('/api/settings')]).then(([m, s]) => {
      setMeta(m)
      setLang(s.default_language || 'auto')
      if (s.default_language && s.default_language !== 'auto') setUiLang(s.default_language)
    })
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {})
  }, [])

  // Evening reminder: once a day after closing time, list customers without phone numbers and pending orders.
  useEffect(() => {
    if (!meta) return
    const check = async () => {
      const today = new Date().toISOString().slice(0, 10)
      let seen = null
      try { seen = localStorage.getItem('bk_evening') } catch { /* storage blocked */ }
      if (seen === today) return
      const { closing_time: close } = await api('/api/settings')
      const now = new Date()
      if (`${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}` < close) return
      const e = await api(`/api/evening?lang=${uiLangRef.current}`)
      if (!e.missing.length && !e.orders.length) return
      setEvening(e)
      voice.current?.sendJson({ type: 'evening' })
      try { localStorage.setItem('bk_evening', today) } catch { /* storage blocked */ }
    }
    check()
    const id = setInterval(check, 60000)
    return () => clearInterval(id)
  }, [meta, started])
  const uiLangRef = useRef(uiLang)
  uiLangRef.current = uiLang

  const t = (k) => meta?.ui[uiLang]?.[k] ?? meta?.ui.en[k] ?? k
  const patch = (p) => setConv((c) => ({ ...c, ...p }))

  function onEvent(m) {
    switch (m.type) {
      case 'transcript':
        // new request: clear the previous reply so it can't be mistaken for this one
        setConv((c) => ({ ...c, transcript: m.text, reply: null, thinking: true, latency: { stt: m.stt_ms } }))
        break
      case 'ignored':
        patch({ thinking: false })
        break
      case 'reply':
        setUiLang(m.lang)
        if (!m.evening) patch({ reply: m, notice: '', thinking: false })
        if (m.source) setConv((c) => ({ ...c, latency: { ...c.latency, source: m.source, brain: m.brain_ms } }))
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
        patch({ notice: t('noMic'), listening: false })
        break
    }
  }

  function start() {
    voice.current = new VoiceClient((m) => onEventRef.current(m), { engine, lang, bargeIn })
    voice.current.connect()
    setStarted(true)
  }
  const onEventRef = useRef(onEvent)
  onEventRef.current = onEvent

  async function toggleMic() {
    const v = voice.current
    if (conv.listening) {
      patch({ listening: false })
      await v.micStop()
    } else if (await v.micStart()) {
      patch({ listening: true })
    }
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
    if (l !== 'auto') setUiLang(l)
    voice.current?.setConfig({ lang: l })
  }

  function toggleBrain() {
    setBrainOn(!brainOn)
    voice.current?.setConfig({ brain: !brainOn })
  }

  function toggleBarge() {
    setBargeIn(!bargeIn)
    voice.current?.setConfig({ bargeIn: !bargeIn })
  }

  if (!meta) return <div className="splash">BolKhata…</div>

  return (
    <div className="app">
      <header className="bar">
        <h1>BolKhata</h1>
        <select aria-label={t('language')} value={lang} onChange={(e) => changeLang(e.target.value)}>
          {Object.entries(LANG_NAMES).map(([k, v]) => <option key={k} value={k}>{k === 'auto' ? t('auto') : v}</option>)}
        </select>
        <button className="chip" onClick={cycleEngine} title={`Voice engine: ${ENGINE_NAMES[engine]}`}>{ENGINE_SHORT[engine]}</button>
        <button className={`chip ${bargeIn ? 'on' : ''}`} aria-pressed={bargeIn} onClick={toggleBarge} title={t('bargeIn')}>🗣</button>
        {meta.llm && meta.llm.length > 0 && (
          <button className={`chip ${brainOn ? 'on' : ''}`} aria-pressed={brainOn} onClick={toggleBrain} title={t('brain')}>🧠</button>
        )}
      </header>

      <main>
        {evening && tab === 'home' && (
          <div className="evening" role="status">
            <b>🌙 {t('eveningTitle')}</b>
            <p>{evening.text}</p>
            <div className="chips">
              {evening.missing.map((c) => (
                <button key={c.id} className="chip big" onClick={() => { setOpenCustomer(c.id); setTab('customers') }}>
                  📞 {c.name}{c.note && ` · ${c.note}`}
                </button>
              ))}
              {evening.orders.length > 0 && <button className="chip big" onClick={() => setTab('orders')}>📦 {t('orders')}</button>}
            </div>
            <button className="btn" onClick={() => setEvening(null)}>{t('dismiss')}</button>
          </div>
        )}
        {tab === 'home' && (started
          ? <Home t={t} conv={conv} voice={voice.current} toggleMic={toggleMic} lang={lang} uiLang={uiLang}
              onSubmit={(said) => patch({ transcript: said, reply: null, thinking: true })} />
          : <div className="start"><p>{meta.ui[uiLang].tapToSpeak}</p><button className="mic" onClick={start} aria-label="Start">🎤</button></div>)}
        {tab === 'customers' && <Customers t={t} uiLang={uiLang} open={openCustomer} setOpen={setOpenCustomer} />}
        {tab === 'orders' && <Orders t={t} uiLang={uiLang} />}
        {tab === 'ledger' && <Ledger t={t} />}
        {tab === 'settings' && <Settings t={t} meta={meta} />}
      </main>

      <nav className="tabs">
        {[['home', '🎤'], ['customers', '👥'], ['orders', '📦'], ['ledger', '📊'], ['settings', '⚙️']].map(([k, icon]) => (
          <button key={k} className={tab === k ? 'active' : ''} onClick={() => setTab(k)}>
            <span>{icon}</span>{t(k)}
          </button>
        ))}
      </nav>
    </div>
  )
}

function Home({ t, conv, voice, toggleMic, lang, uiLang, onSubmit }) {
  const [text, setText] = useState('')
  const [editing, setEditing] = useState(false)
  const [amount, setAmount] = useState('')
  const r = conv.reply
  const card = r?.state === 'confirming' ? r.card : null
  const [undoLeft, setUndoLeft] = useState(0)
  useEffect(() => {
    if (!r?.saved || !r.undo) { setUndoLeft(0); return }
    const until = Date.now() + r.undo * 1000
    const tick = () => setUndoLeft(Math.max(0, Math.ceil((until - Date.now()) / 1000)))
    tick()
    const id = setInterval(tick, 250)
    return () => clearInterval(id)
  }, [r])
  const money = card && !['order', 'arrival', 'phone'].includes(card.type)

  async function notify(cid) {
    const { url } = await api(`/api/customers/${cid}/arrived-message?lang=${uiLang}`)
    window.open(url, '_blank', 'noopener') // WhatsApp opens with the text ready; the shopkeeper presses send
  }

  const lastSent = useRef({ text: '', at: 0 })
  function send(e) {
    e.preventDefault()
    const t2 = text.trim()
    if (!t2) return
    if (t2 === lastSent.current.text && Date.now() - lastSent.current.at < 1500) return // accidental double send
    lastSent.current = { text: t2, at: Date.now() }
    onSubmit(t2) // clear the old reply now; the newest request always wins
    voice.sendText(t2)
    setText('')
  }

  function saveAmount(e) {
    e.preventDefault()
    const n = parseInt(amount, 10)
    if (n > 0) voice.tap('amount', { amount: n })
    setEditing(false)
  }

  return (
    <div className="home">
      <div className="status">
        <span className="chip small">{t('detected')}: {LANG_NAMES[r?.lang || (lang === 'auto' ? 'hi' : lang)]}</span>
        <span className="latency">
          STT {conv.latency.stt ?? '—'} ms · reply {conv.latency.reply ?? '—'} ms
          {conv.latency.source && ` · ${conv.latency.source === 'rules' ? 'rules' : `${conv.latency.source} ${conv.latency.brain} ms`}`}
        </span>
      </div>

      <button className={`mic ${conv.listening ? 'live' : ''} ${conv.speaking ? 'speaking' : ''}`} onClick={toggleMic}
        aria-label={conv.listening ? t('listening') : t('tapToSpeak')}>🎤</button>
      <p className="hint">{conv.listening ? t('listening') : t('tapToSpeak')}</p>

      {conv.notice && <p className="notice" role="status">{conv.notice}</p>}
      {conv.transcript && <p className="transcript">“{conv.transcript}”</p>}
      {conv.thinking && !r && <div className="reply thinking" aria-live="polite">{t('thinking')}</div>}
      {r && <div className={`reply ${r.saved ? 'ok' : ''}`} aria-live="polite">{r.text}</div>}
      {r?.notify && <button className="btn primary wide" onClick={() => notify(r.notify)}>💬 {t('notifyCustomer')}</button>}
      {undoLeft > 0 && (
        <button className="btn wide" onClick={() => { setUndoLeft(0); voice.tap('undo') }}>↩ {t('undo')} ({undoLeft})</button>
      )}

      {r?.state === 'chooseCustomer' && (
        <div className="chips">
          {r.options.map((o, i) => <button key={i} className="chip big" onClick={() => voice.tap('choose', { index: i })}>{o}</button>)}
        </div>
      )}

      {card && (
        <div className={`confirm ${card.type}`}>
          <div className="who">{card.name}{card.note && <small> · {card.note}</small>}{card.isNew && <span className="tag">{t('newCustomer')}</span>}</div>
          <div className="type">{t(card.type)}</div>
          {money ? <div className="amount">₹{card.amount}</div> : <div className="items">{card.type === 'phone' ? `📞 ${card.phone}` : card.items}</div>}
          {editing ? (
            <form onSubmit={saveAmount} className="row">
              <input type="number" inputMode="numeric" min="1" step="1" autoFocus value={amount}
                onChange={(e) => setAmount(e.target.value)} aria-label={t('amount')} />
              <button className="btn primary">OK</button>
            </form>
          ) : (
            <div className="row">
              <button className="btn primary" onClick={() => voice.tap('save')}>{t('save')}</button>
              <button className="btn" onClick={() => voice.tap('cancel')}>{t('cancel')}</button>
              {money && <button className="btn" onClick={() => { setAmount(String(card.amount)); setEditing(true) }}>{t('editAmount')}</button>}
            </div>
          )}
        </div>
      )}

      <form className="typebox" onSubmit={send}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder={t('typeHere')} aria-label={t('typeHere')} />
        <button className="btn primary">{t('send')}</button>
      </form>
    </div>
  )
}
