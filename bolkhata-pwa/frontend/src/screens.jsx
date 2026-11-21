import { useEffect, useState } from 'react'
import { LANG_NAMES, api } from './App.jsx'

const time = (iso) => new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
const money = (n) => `₹${n}`

const day = (iso) => (iso ? new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : '—')

export function Customers({ t, uiLang, open, setOpen }) {
  const [list, setList] = useState([])
  const [q, setQ] = useState('')
  const [byBalance, setByBalance] = useState(true)
  useEffect(() => { api('/api/customers').then(setList) }, [open])

  if (open) return <History t={t} id={open} uiLang={uiLang} back={() => setOpen(null)} />
  const shown = list
    .filter((c) => `${c.name} ${c.note}`.toLowerCase().includes(q.toLowerCase()))
    .sort((a, b) => (byBalance ? b.balance - a.balance : a.name.localeCompare(b.name)))
  return (
    <div className="page">
      <div className="row">
        <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('search')} aria-label={t('search')} />
        <button className="btn" onClick={() => setByBalance(!byBalance)}>{byBalance ? t('sortBalance') : t('sortName')}</button>
      </div>
      <ul className="list">
        {shown.map((c) => (
          <li key={c.id}>
            <button onClick={() => setOpen(c.id)}>
              <span>{c.name}{c.note && <small> · {c.note}</small>}{c.demo && <span className="tag">{t('demoData')}</span>}
                <br /><small className="muted">{t('lastVisit')}: {day(c.last_visit)}{!c.phone && ' · 📞 —'}</small></span>
              <b className={c.balance > 0 ? 'owes' : 'adv'}>{money(c.balance)}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function History({ t, id, uiLang, back }) {
  const [c, setC] = useState(null)
  const [phone, setPhone] = useState('')
  const [note, setNote] = useState('')
  const [err, setErr] = useState('')
  const [ok, setOk] = useState(false)
  useEffect(() => { api(`/api/customers/${id}`).then((x) => { setC(x); setPhone(x.phone || ''); setNote(x.note || '') }) }, [id])
  if (!c) return null

  async function saveDetails(e) {
    e.preventDefault()
    try {
      const x = await api(`/api/customers/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, note }) })
      setC({ ...c, phone: x.phone, note: x.note })
      setErr('')
      setOk(true)
    } catch (e2) { setErr(e2.message); setOk(false) }
  }

  async function remind() {
    try {
      const { url } = await api(`/api/customers/${id}/reminder?lang=${uiLang}`)
      window.open(url, '_blank', 'noopener') // opens WhatsApp with the text filled in; the shopkeeper presses send
    } catch (e2) { setErr(e2.message) }
  }

  return (
    <div className="page">
      <button className="btn" onClick={back}>← {t('back')}</button>
      <h2>{c.name}{c.note && <small> · {c.note}</small>}</h2>
      <p className={`big ${c.balance > 0 ? 'owes' : 'adv'}`}>{t('balance')}: {money(c.balance)}</p>
      <form className="form" onSubmit={saveDetails}>
        <label>{t('phone')}<input type="tel" inputMode="numeric" value={phone} onChange={(e) => { setPhone(e.target.value); setOk(false) }} /></label>
        <label>{t('area')}<input value={note} onChange={(e) => { setNote(e.target.value); setOk(false) }} /></label>
        <button className="btn wide">{t('save')}</button>
        {ok && <p className="notice ok">{t('saved')}</p>}
      </form>
      {c.balance > 0 && c.phone && <button className="btn primary wide" onClick={remind}>💬 {t('remind')}</button>}
      {err && <p className="notice">{err}</p>}
      <ul className="history">
        {c.history.map((e) => (
          <li key={e.id}>
            <div><b className={e.type === 'credit' ? 'owes' : 'adv'}>{e.type === 'credit' ? '+' : '−'}{money(e.amount)}</b> <small>{t(e.type)} · {time(e.created_at)}</small></div>
            <div className="said">“{e.raw_text}”</div>
            <small>{t('running')}: {money(e.running)}</small>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function Orders({ t, uiLang }) {
  const [list, setList] = useState(null)
  const [err, setErr] = useState('')
  const load = () => api('/api/orders').then(setList)
  useEffect(() => { load() }, [])
  if (!list) return null

  async function setStatus(o, status) {
    await api(`/api/orders/${o.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) })
    load()
  }
  async function notify(o) {
    try {
      const { url } = await api(`/api/customers/${o.customer_id}/arrived-message?lang=${uiLang}`)
      window.open(url, '_blank', 'noopener') // the shopkeeper presses send in WhatsApp
    } catch (e) { setErr(e.message) }
  }
  const row = (o, actions) => (
    <li key={o.id}>
      <div><b>{o.customer}</b>{o.note && <small> · {o.note}</small>} <small className="muted">{time(o.created_at)}</small></div>
      <div className="said">{o.items}</div>
      <div className="row">{actions}</div>
    </li>
  )
  const pending = list.filter((o) => o.status === 'pending')
  const arrived = list.filter((o) => o.status === 'arrived')
  return (
    <div className="page">
      {err && <p className="notice">{err}</p>}
      <h2>{t('pendingOrders')} ({pending.length})</h2>
      <ul className="history">
        {pending.map((o) => row(o, <button className="btn primary" onClick={() => setStatus(o, 'arrived')}>📦 {t('markArrived')}</button>))}
      </ul>
      <h2>{t('arrivedOrders')} ({arrived.length})</h2>
      <ul className="history">
        {arrived.map((o) => row(o, <>
          {o.phone && <button className="btn primary" onClick={() => notify(o)}>💬 {t('notifyCustomer')}</button>}
          <button className="btn" onClick={() => setStatus(o, 'closed')}>✓ {t('markDelivered')}</button>
        </>))}
      </ul>
    </div>
  )
}

export function Ledger({ t }) {
  const [data, setData] = useState(null)
  const [f, setF] = useState({ q: '', type: '', lang: '' })
  useEffect(() => { api('/api/ledger').then(setData) }, [])
  if (!data) return null
  const rows = data.entries.filter((e) =>
    e.customer.toLowerCase().includes(f.q.toLowerCase()) && (!f.type || e.type === f.type) && (!f.lang || e.language === f.lang))
  return (
    <div className="page">
      <div className="summary">
        <div><small>{t('creditGiven')}</small><b className="owes">{money(data.today.credit)}</b></div>
        <div><small>{t('paymentsReceived')}</small><b className="adv">{money(data.today.payment)}</b></div>
        <div><small>{t('net')}</small><b>{money(data.today.net)}</b></div>
      </div>
      <p className="muted">{t('today')}</p>
      <div className="row wrap">
        <input type="search" value={f.q} onChange={(e) => setF({ ...f, q: e.target.value })} placeholder={t('customer')} aria-label={t('customer')} />
        <select value={f.type} onChange={(e) => setF({ ...f, type: e.target.value })} aria-label={t('type')}>
          <option value="">{t('all')}</option><option value="credit">{t('credit')}</option><option value="payment">{t('payment')}</option>
        </select>
        <select value={f.lang} onChange={(e) => setF({ ...f, lang: e.target.value })} aria-label={t('language')}>
          <option value="">{t('all')}</option>
          {Object.entries(LANG_NAMES).filter(([k]) => k !== 'auto').map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <a className="btn primary" href="/api/ledger.csv" download>⬇ {t('export')}</a>
      </div>
      <div className="tablewrap">
        <table>
          <thead><tr><th>{t('customer')}</th><th>{t('type')}</th><th>{t('amount')}</th><th>{t('language')}</th><th>{t('time')}</th></tr></thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td>{e.customer}</td>
                <td>{t(e.type)}</td>
                <td className={e.type === 'credit' ? 'owes' : 'adv'}>{money(e.amount)}</td>
                <td>{LANG_NAMES[e.language] || e.language}</td>
                <td>{time(e.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export function Settings({ t, meta }) {
  const [s, setS] = useState(null)
  const [done, setDone] = useState(false)
  useEffect(() => { api('/api/settings').then(setS) }, [])
  if (!s) return null
  async function save(e) {
    e.preventDefault()
    setS(await api('/api/settings', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(s) }))
    setDone(true)
  }
  const field = (k) => ({ value: s[k], onChange: (e) => { setS({ ...s, [k]: e.target.value }); setDone(false) } })
  return (
    <form className="page form" onSubmit={save}>
      <label>{t('shopName')}<input {...field('shop_name')} /></label>
      <label>{t('upiVpa')}<input {...field('upi_vpa')} placeholder="shop@upi" /></label>
      <label>{t('defaultLanguage')}
        <select {...field('default_language')}>
          {Object.entries(LANG_NAMES).map(([k, v]) => <option key={k} value={k}>{k === 'auto' ? t('auto') : v}</option>)}
        </select>
      </label>
      <label>{t('closingTime')}<input type="time" {...field('closing_time')} /></label>
      <label>{t('regionalLanguage')}
        <select {...field('regional_language')}>
          <option value="">{t('none')}</option>
          {['kn', 'te', 'ta'].map((k) => <option key={k} value={k}>{LANG_NAMES[k]}</option>)}
        </select>
      </label>
      <button className="btn primary wide">{t('save')}</button>
      {done && <p className="notice ok">{t('saved')}</p>}
      <p className="muted">{meta.seed_demo ? t('demoOn') : t('demoOff')}</p>
    </form>
  )
}
