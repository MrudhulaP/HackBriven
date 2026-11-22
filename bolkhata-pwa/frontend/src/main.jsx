import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { ErrorBoundary, reportError } from './ErrorBoundary.jsx'
import './styles.css'

window.addEventListener('error', (e) => reportError('error', e.message, e.error?.stack))
window.addEventListener('unhandledrejection', (e) => reportError('promise', e.reason?.message || e.reason, e.reason?.stack))

createRoot(document.getElementById('root')).render(<ErrorBoundary onRetry={() => location.reload()}><App /></ErrorBoundary>)
