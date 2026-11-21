import { useEffect, useRef, useState } from 'react'
import { Icon } from './Icon.jsx'
import { LANG_NAMES, api } from './App.jsx'

// Example commands shown before the first sentence; tapping one sends it through the real assistant.
const EXAMPLES = {
  en: ['Lakshmi took 200 on credit', 'Who owes me the most?', "Show today's collections"],
  hi: ['Lakshmi ne 200 udhaar liya', 'Sabse zyada baaki kiska hai?', 'Aaj kitna mila?'],
  kn: ['ಲಕ್ಷ್ಮಿ 200 ಸಾಲ ತಗೊಂಡ್ರು', 'ಲಕ್ಷ್ಮಿ ಬಾಕಿ ಎಷ್ಟು', 'ಒಟ್ಟು ಬಾಕಿ ಎಷ್ಟು'],
  te: ['లక్ష్మి 200 అప్పు తీసుకున్నారు', 'లక్ష్మి బాకీ ఎంత', 'మొత్తం బాకీ ఎంత'],
  ta: ['லக்ஷ்மி 200 கடன் வாங்கினார்', 'லக்ஷ்மி நிலுவை எவ்வளவு', 'மொத்த நிலுவை எவ்வளவு'],
}
const ENGINE_SHORT = { live: 'Live', rest: 'REST', browser: 'Web' }
const ENGINE_NAMES = { live: 'Gnani Live', rest: 'Gnani REST', browser: 'Browser speech' }

/** idle | listening | processing | speaking | error | off — one visible state at a time. */
export function voiceState(conv, started) {
  if (!started) return 'off'
  if (conv.failed && !conv.thinking) return 'error'
  if (conv.thinking) return 'processing'
  if (conv.speaking) return 'speaking'
  if (conv.listening) return 'listening'
  return 'idle'
}

/**
 * The rings: a closed waveform loop around the mic whose shape follows the real audio — the shopkeeper's voice
 * while listening, the reply while speaking. Reads the analyser that already sits on the one mic stream.
 */
function Rings({ voice, state }) {
  const ref = useRef(null)
  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    const size = canvas.clientWidth
    canvas.width = canvas.height = size * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    const c = size / 2
    const base = size * 0.2
    let raf = 0
    let energy = 0
    const smooth = new Float32Array(48)

    const loop = (radius, amp, color, width, glow, phase) => {
      ctx.beginPath()
      const n = smooth.length
      for (let i = 0; i <= n * 2; i++) {
        const a = (i / (n * 2)) * Math.PI * 2
        const k = smooth[Math.floor(i / 2) % n]
        const r = radius + amp * k * (0.75 + 0.25 * Math.sin(a * 3 + phase))
        const x = c + r * Math.cos(a)
        const y = c + r * Math.sin(a)
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.closePath()
      ctx.strokeStyle = color
      ctx.lineWidth = width
      ctx.shadowColor = color
      ctx.shadowBlur = glow
      ctx.stroke()
    }

    const draw = (time) => {
      ctx.clearRect(0, 0, size, size)
      const t = time / 1000
      if (state === 'listening' || state === 'speaking') {
        const bins = voice?.levels()
        let sum = 0
        for (let i = 0; i < smooth.length; i++) {
          // mirror the spectrum around the circle so the loop stays balanced
          const v = bins ? bins[Math.min(bins.length - 1, 2 + (i < smooth.length / 2 ? i : smooth.length - i))] / 255 : 0
          smooth[i] += (v - smooth[i]) * 0.35
          sum += smooth[i]
        }
        energy += (sum / smooth.length - energy) * 0.2
        const spread = size * 0.16
        const gold = state === 'listening' ? '226,179,60' : '159,214,181'
        loop(base + 10 + energy * 14, spread, `rgba(${gold},0.95)`, 2.5, 18, t * 2)
        loop(base + 22 + energy * 22, spread * 0.8, `rgba(${gold},0.45)`, 1.5, 10, t * 1.4 + 1)
        loop(base + 34 + energy * 30, spread * 0.6, `rgba(${gold},0.22)`, 1, 0, t + 2)
      } else if (state === 'processing') {
        ctx.shadowBlur = 0
        for (let i = 0; i < 3; i++) {
          const start = (reduce ? 0 : t * (1.6 - i * 0.35)) + i * 2.1
          ctx.beginPath()
          ctx.arc(c, c, base + 12 + i * 12, start, start + 1.1)
          ctx.strokeStyle = `rgba(226,179,60,${0.9 - i * 0.28})`
          ctx.lineWidth = 2.5 - i * 0.6
          ctx.stroke()
        }
      } else {
        const breathe = reduce || state === 'off' ? 0 : Math.sin(t * 1.3) * 2
        ctx.beginPath()
        ctx.arc(c, c, base + 12 + breathe, 0, Math.PI * 2)
        ctx.strokeStyle = state === 'error' ? 'rgba(255,140,120,0.6)' : 'rgba(226,179,60,0.35)'
        ctx.lineWidth = 1.5
        ctx.shadowBlur = 0
        ctx.stroke()
      }
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(raf)
  }, [voice, state])
  return <canvas ref={ref} className="rings" aria-hidden="true" />
}

export function VoiceConsole({ t, conv, voice, started, onStart, onMic, onSubmit, lang, uiLang, engine, onEngine,
  bargeIn, onBarge, brainOn, onBrain, llm }) {
  const [text, setText] = useState('')
  const [editing, setEditing] = useState(false)
  const [amount, setAmount] = useState('')
  const [undoLeft, setUndoLeft] = useState(0)
  const r = conv.reply
  const card = r?.state === 'confirming' ? r.card : null
  const money = card && !['order', 'arrival', 'phone'].includes(card.type)
  const state = voiceState(conv, started)
  const lastSent = useRef({ text: '', at: 0 })

  useEffect(() => {
    if (!r?.saved || !r.undo) { setUndoLeft(0); return }
    const until = Date.now() + r.undo * 1000
    const tick = () => setUndoLeft(Math.max(0, Math.ceil((until - Date.now()) / 1000)))
    tick()
    const id = setInterval(tick, 250)
    return () => clearInterval(id)
  }, [r])
  useEffect(() => { setEditing(false) }, [r])

  function send(e) {
    e.preventDefault()
    const said = text.trim()
    if (!said) return
    if (said === lastSent.current.text && Date.now() - lastSent.current.at < 1500) return // accidental double send
    lastSent.current = { text: said, at: Date.now() }
    onSubmit(said)
    setText('')
  }

  async function notify(cid) {
    try {
      const { url } = await api(`/api/customers/${cid}/arrived-message?lang=${uiLang}`)
      window.open(url, '_blank', 'noopener') // WhatsApp opens with the text ready; the shopkeeper presses send
    } catch { /* the reply already says how to add a number */ }
  }

  const status = {
    off: t('tapToStart'), idle: t('tapToSpeak'), listening: t('tapToStop'), processing: t('processing'),
    speaking: r?.text ? '' : t('tapToSpeak'), error: t('failed'),
  }[state]
  const detected = LANG_NAMES[r?.lang || (lang === 'auto' ? 'en' : lang)]

  return (
    <section className={`console is-${state}`} aria-label="Voice assistant">
      <div className="console-meta">
        <span className="lang-pill" title={t('detected')}>{lang === 'auto' ? `${t('auto')}: ${detected}` : detected}</span>
        {conv.latency.source && (
          <span className="latency">
            {conv.latency.source === 'rules' ? 'rules' : `${conv.latency.source} ${conv.latency.brain} ms`}
            {conv.latency.reply != null && ` · ${conv.latency.reply} ms`}
          </span>
        )}
      </div>

      <div className="dialogue" aria-live="polite">
        {conv.transcript && <p className="said">{conv.transcript}</p>}
        {state === 'processing' && !r && <p className="answer muted-answer">{t('processing')}</p>}
        {r && <p className={`answer ${r.saved ? 'is-saved' : ''}`}>{r.text}</p>}
        {state === 'error' && (
          <p className="answer is-error" role="alert">
            {t('failed')}{' '}
            {conv.lastSaid && <button className="link" onClick={() => onSubmit(conv.lastSaid)}>{t('retry')}</button>}
          </p>
        )}
        {!conv.transcript && !r && state !== 'error' && state !== 'processing' && (
          <div className="examples">
            <p>{t('trySaying')}</p>
            {(EXAMPLES[uiLang] || EXAMPLES.en).map((ex) => (
              <button key={ex} className="example" onClick={() => onSubmit(ex)}>“{ex}”</button>
            ))}
          </div>
        )}
        {(conv.notice || conv.offline) && <p className="console-notice" role="status">{conv.offline ? t('offline') : conv.notice}</p>}

        {r?.state === 'chooseCustomer' && (
          <div className="choices">
            {r.options.map((o, i) => <button key={i} className="choice" onClick={() => voice.tap('choose', { index: i })}>{o}</button>)}
          </div>
        )}

        {card && (
          <div className={`confirm kind-${card.type}`}>
            <div className="confirm-head">
              <span className="confirm-who">{card.name}{card.note && <small>{card.note}</small>}</span>
              <span className="confirm-kind">{t(card.type)}{card.isNew && <em>{t('newCustomer')}</em>}</span>
            </div>
            <div className="confirm-value">
              {money ? `₹${card.amount}` : card.type === 'phone' ? card.phone : card.items}
            </div>
            {editing ? (
              <form className="confirm-actions" onSubmit={(e) => {
                e.preventDefault()
                const n = parseInt(amount, 10)
                if (n > 0) voice.tap('amount', { amount: n })
                setEditing(false)
              }}>
                <input type="number" inputMode="numeric" min="1" step="1" autoFocus value={amount}
                  onChange={(e) => setAmount(e.target.value)} aria-label={t('amount')} />
                <button className="btn solid">OK</button>
              </form>
            ) : (
              <div className="confirm-actions">
                <button className="btn solid" onClick={() => voice.tap('save')}>{t('save')}</button>
                <button className="btn ghost" onClick={() => voice.tap('cancel')}>{t('cancel')}</button>
                {money && <button className="btn ghost" onClick={() => { setAmount(String(card.amount)); setEditing(true) }}>{t('editAmount')}</button>}
              </div>
            )}
          </div>
        )}

        {(r?.notify || undoLeft > 0) && (
          <div className="after-save">
            {r?.notify && <button className="btn solid" onClick={() => notify(r.notify)}><Icon name="chat" /> {t('notifyCustomer')}</button>}
            {undoLeft > 0 && <button className="btn ghost" onClick={() => { setUndoLeft(0); voice.tap('undo') }}>{t('undo')} ({undoLeft})</button>}
          </div>
        )}
      </div>

      <div className="mic-stage">
        <Rings voice={voice} state={state} />
        <button className="mic-btn" onClick={started ? onMic : onStart}
          aria-label={state === 'listening' ? t('tapToStop') : started ? t('tapToSpeak') : t('tapToStart')}
          aria-pressed={state === 'listening'}>
          <Icon name={state === 'listening' ? 'stop' : 'mic'} size={30} />
        </button>
      </div>
      <p className="mic-status" aria-live="polite">{status}</p>

      <form className="type-row" onSubmit={send}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder={t('typeHere')} aria-label={t('typeHere')}
          enterKeyHint="send" />
        <button className="btn solid" aria-label={t('send')}><Icon name="send" /></button>
      </form>

      <div className="console-tools">
        <button className="tool" onClick={onEngine} title={`Voice engine: ${ENGINE_NAMES[engine]}`}>{ENGINE_SHORT[engine]}</button>
        <button className={`tool ${bargeIn ? 'on' : ''}`} aria-pressed={bargeIn} onClick={onBarge} title={t('bargeIn')}>{t('bargeIn')}</button>
        {llm && <button className={`tool ${brainOn ? 'on' : ''}`} aria-pressed={brainOn} onClick={onBrain} title={t('brain')}>{t('brain')}</button>}
      </div>
    </section>
  )
}
