import { Component } from 'react'

// Last line of defence: one broken screen must never blank the whole app. The real error is reported to the
// backend log (no stack trace is shown to the shopkeeper) so the cause can be fixed.
export function reportError(kind, message, stack) {
  try {
    fetch('/api/client-error', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind, message: String(message).slice(0, 500), stack: String(stack || '').slice(0, 2000), url: location.pathname }),
    }).catch(() => {})
  } catch { /* reporting must never throw */ }
}

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { failed: false }
  }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error, info) {
    reportError('render', error?.message || error, (error?.stack || '') + (info?.componentStack || ''))
  }

  render() {
    if (!this.state.failed) return this.props.children
    return (
      <div className="crash" role="alert">
        <p>{this.props.message || 'Something went wrong while processing your request. Please try again.'}</p>
        <button className="btn primary" onClick={() => { this.setState({ failed: false }); this.props.onRetry?.() }}>
          {this.props.retry || 'Try again'}
        </button>
      </div>
    )
  }
}
