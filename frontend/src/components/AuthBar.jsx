import { useEffect, useState } from 'react'
import api from '../api.js'

export function AuthBar() {
  const [email, setEmail] = useState(localStorage.getItem('trustdoc_email') || 'admin@trustdoc.local')
  const [password, setPassword] = useState('admin123')
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('')

  async function loadMe() {
    try {
      const res = await api.get('/api/auth/me')
      setUser(res.data)
    } catch (_) {
      setUser(null)
    }
  }

  useEffect(() => { loadMe() }, [])

  async function login(e) {
    e.preventDefault()
    setStatus('Signing in...')
    try {
      const res = await api.post('/api/auth/login', { email, password })
      localStorage.setItem('trustdoc_token', res.data.access_token)
      localStorage.setItem('trustdoc_email', res.data.email)
      setUser(res.data)
      setStatus(res.data.auth_enabled ? 'Authenticated demo session active.' : 'Demo login saved. Auth enforcement is off for local development.')
    } catch (err) {
      setStatus(err.response?.data?.detail || err.message)
    }
  }

  function logout() {
    localStorage.removeItem('trustdoc_token')
    localStorage.removeItem('trustdoc_email')
    setUser(null)
    setStatus('Signed out locally.')
  }

  return (
    <section className="auth-bar">
      <div>
        <strong>Demo access</strong>
        <span>{user ? `${user.email} · ${user.role}` : 'Local demo admin available'}</span>
      </div>
      <form onSubmit={login} className="auth-form">
        <input value={email} onChange={(e) => setEmail(e.target.value)} aria-label="email" />
        <input value={password} type="password" onChange={(e) => setPassword(e.target.value)} aria-label="password" />
        <button type="submit" className="ghost">Login</button>
        <button type="button" className="ghost" onClick={logout}>Logout</button>
      </form>
      {status && <small className="muted">{status}</small>}
    </section>
  )
}
