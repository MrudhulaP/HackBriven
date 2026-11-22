import { useEffect, useState } from 'react'
import { Icon } from './Icon.jsx'
import { api } from './App.jsx'

const rupees = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`
const fill = (s, vars) => Object.entries(vars).reduce((acc, [k, v]) => acc.replace(`{${k}}`, v), s)
const istDay = (d) => new Date(d.getTime() + 330 * 60000).toISOString().slice(0, 10)

// Quick actions become ordinary commands, so they go through the same confirm-before-save step as voice.
const TEMPLATES = {
  credit: { en: '{n} took {a} on credit', hi: '{n} ne {a} udhaar liya', kn: '{n} {a} ಸಾಲ ತಗೊಂಡ್ರು', te: '{n} {a} అప్పు తీసుకున్నారు', ta: '{n} {a} கடன் வாங்கினார்' },
  payment: { en: '{n} paid {a}', hi: '{n} ne {a} jama kiya', kn: '{n} {a} ಕೊಟ್ಟರು', te: '{n} {a} ఇచ్చారు', ta: '{n} {a} கொடுத்தார்' },
  customer: { en: "Save {n}'s number as {p}", hi: '{n} ka number {p} save karo', kn: '{n} ನಂಬರ್ {p} ಸೇವ್ ಮಾಡಿ', te: '{n} నంబర్ {p} సేవ్ చేయండి', ta: '{n} நம்பர் {p} சேவ் பண்ணுங்க' },
}

/** Everything on the home screen is computed from the ledger itself: entries are the one source of truth. */
export function useDashboard(version) {
  const [data, setData] = useState(null)
  const [err, setErr] = useState(false)
  const load = () => {
    setErr(false)
    Promise.all([api('/api/customers'), api('/api/ledger'), api('/api/orders')])
      .then(([customers, ledger, orders]) => setData({ customers, ledger, orders }))
      .catch(() => setErr(true))
  }
  useEffect(load, [version])
  return { data, err, reload: load }
}

export function Greeting({ t, shop }) {
  const h = new Date().getHours()
  const hello = h < 12 ? t('goodMorning') : h < 17 ? t('goodAfternoon') : t('goodEvening')
  return (
    <div className="greeting">
      <h1>{hello}</h1>
      <p>{fill(t('todayIn'), { shop: shop || 'BolKhata' })}</p>
    </div>
  )
}

export function Summary({ t, data }) {
  const owing = data.customers.filter((c) => c.balance > 0)
  const outstanding = owing.reduce((s, c) => s + c.balance, 0)
  const { credit, payment } = data.ledger.today
  return (
    <dl className="overview">
      <div className="stat stat-lead">
        <dt>{t('outstanding')}</dt>
        <dd>{rupees(outstanding)}</dd>
        <span className="stat-note">{fill(t('owingCount'), { n: owing.length })}</span>
      </div>
      <div className="stat"><dt>{t('todayCredit')}</dt><dd className="ink-credit">{rupees(credit)}</dd></div>
      <div className="stat"><dt>{t('todayCollections')}</dt><dd className="ink-paid">{rupees(payment)}</dd></div>
      <div className="stat">
        <dt>{t('totalCustomers')}</dt><dd>{data.customers.length}</dd>
        <span className="stat-note">{fill(t('withDues'), { n: owing.length })}</span>
      </div>
    </dl>
  )
}

export function QuickActions({ t, onAction, onLedger }) {
  return (
    <div className="quick">
      <button className="quick-btn" onClick={() => onAction('credit')}><Icon name="credit" />{t('addCredit')}</button>
      <button className="quick-btn" onClick={() => onAction('payment')}><Icon name="payment" />{t('recordPayment')}</button>
      <button className="quick-btn" onClick={() => onAction('customer')}><Icon name="phone" />{t('addCustomer')}</button>
      <button className="quick-btn" onClick={onLedger}><Icon name="book" />{t('viewLedger')}</button>
    </div>
  )
}

/** A small form that turns into a spoken-style command; the assistant then asks to confirm it. */
export function ActionSheet({ t, kind, uiLang, customers, onSend, onClose }) {
  const [name, setName] = useState('')
  const [value, setValue] = useState('')
  const isCustomer = kind === 'customer'
  const title = { credit: t('addCredit'), payment: t('recordPayment'), customer: t('addCustomer') }[kind]
  function submit(e) {
    e.preventDefault()
    const n = name.trim()
    const v = value.trim()
    if (!n || !v) return
    const tpl = TEMPLATES[kind][uiLang] || TEMPLATES[kind].en
    onSend(fill(tpl, { n, a: v, p: v.replace(/\D/g, '') }))
  }
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <form className="sheet" onClick={(e) => e.stopPropagation()} onSubmit={submit} aria-label={title}>
        <h2>{title}</h2>
        <label>{t('name')}
          <input value={name} onChange={(e) => setName(e.target.value)} list="bk-customers" autoFocus autoComplete="off" />
        </label>
        <datalist id="bk-customers">
          {[...new Set(customers.map((c) => c.name))].map((n) => <option key={n} value={n} />)}
        </datalist>
        <label>{isCustomer ? t('phone') : t('amount')}
          <input value={value} onChange={(e) => setValue(e.target.value)} inputMode="numeric"
            pattern={isCustomer ? '[0-9 +-]{10,15}' : '[0-9]+'} />
        </label>
        <div className="sheet-actions">
          <button type="button" className="btn plain" onClick={onClose}>{t('cancel')}</button>
          <button className="btn solid">{t('next')}</button>
        </div>
      </form>
    </div>
  )
}

export function RecentEntries({ t, data, onSeeAll }) {
  const rows = data.ledger.entries.slice(0, 6)
  return (
    <section className="panel">
      <header className="panel-head"><h2>{t('recent')}</h2><button className="link" onClick={onSeeAll}>{t('seeAll')}</button></header>
      {rows.length === 0 ? <p className="empty">{t('noEntries')}</p> : (
        <table className="khata">
          <thead><tr><th scope="col">{t('customer')}</th><th scope="col" className="num">{t('credit')}</th><th scope="col" className="num">{t('payment')}</th></tr></thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td>
                  <span className="khata-name">{e.customer}</span>
                  <span className="khata-time">{new Date(e.created_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })}</span>
                </td>
                <td className="num ink-credit">{e.type === 'credit' ? rupees(e.amount) : ''}</td>
                <td className="num ink-paid">{e.type === 'payment' ? rupees(e.amount) : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

export function TopDues({ t, data, onOpen }) {
  const top = data.customers.filter((c) => c.balance > 0).sort((a, b) => b.balance - a.balance).slice(0, 4)
  const max = top[0]?.balance || 1
  return (
    <section className="panel">
      <header className="panel-head"><h2>{t('topDues')}</h2></header>
      {top.length === 0 ? <p className="empty">{t('allClear')}</p> : (
        <ul className="dues">
          {top.map((c) => (
            <li key={c.id}>
              <button onClick={() => onOpen(c.id)}>
                <span className="due-name">{c.name}{c.note && <small>{c.note}</small>}</span>
                <span className="due-amt">{rupees(c.balance)}</span>
                <span className="due-bar" style={{ '--w': `${Math.max(6, (c.balance / max) * 100)}%` }} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function Week({ t, data, pendingOrders, onOrders }) {
  const days = [...Array(7)].map((_, i) => istDay(new Date(Date.now() - (6 - i) * 86400000)))
  const sums = Object.fromEntries(days.map((d) => [d, { credit: 0, payment: 0 }]))
  for (const e of data.ledger.entries) {
    const d = e.created_at.slice(0, 10)
    if (sums[d]) sums[d][e.type] += e.amount
  }
  const max = Math.max(1, ...days.map((d) => Math.max(sums[d].credit, sums[d].payment)))
  const weekPaid = days.reduce((s, d) => s + sums[d].payment, 0)
  const weekGiven = days.reduce((s, d) => s + sums[d].credit, 0)
  const label = (d) => new Date(`${d}T12:00:00+05:30`).toLocaleDateString('en-IN', { weekday: 'narrow' })
  return (
    <section className="panel">
      <header className="panel-head"><h2>{t('thisWeek')}</h2>
        {pendingOrders > 0 && <button className="link" onClick={onOrders}>{t('pendingOrdersN').replace('{n}', pendingOrders)}</button>}
      </header>
      <div className="week-totals">
        <span><i className="key key-paid" />{t('collected')} <b className="ink-paid">{rupees(weekPaid)}</b></span>
        <span><i className="key key-credit" />{t('given')} <b className="ink-credit">{rupees(weekGiven)}</b></span>
      </div>
      <div className="week" role="img" aria-label={`${t('collected')} ${rupees(weekPaid)}, ${t('given')} ${rupees(weekGiven)}`}>
        {days.map((d) => (
          <div className="day" key={d} title={`${d}: ${t('collected')} ${rupees(sums[d].payment)}, ${t('given')} ${rupees(sums[d].credit)}`}>
            <div className="bars">
              <span className="bar bar-paid" style={{ height: `${(sums[d].payment / max) * 100}%` }} />
              <span className="bar bar-credit" style={{ height: `${(sums[d].credit / max) * 100}%` }} />
            </div>
            <span className="day-label">{label(d)}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
