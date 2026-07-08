import { useEffect, useState } from 'react'
import api from '../api.js'

export function Analytics() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  async function loadSummary() {
    setError('')
    try {
      const res = await api.get('/api/analytics/summary')
      setSummary(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  useEffect(() => { loadSummary() }, [])

  return (
    <section className="grid-two">
      <div className="card">
        <div className="space-between">
          <h2>Analytics</h2>
          <button onClick={loadSummary}>Refresh</button>
        </div>
        <p className="muted">Operational metrics from documents, retrieval, and question logs.</p>
        {error && <p className="error">{error}</p>}
        {summary && (
          <div className="metric-grid wide">
            <div><strong>{summary.documents}</strong><span>Documents</span></div>
            <div><strong>{summary.chunks}</strong><span>Chunks</span></div>
            <div><strong>{summary.questions}</strong><span>Questions</span></div>
            <div><strong>{summary.avg_latency_ms}</strong><span>Avg latency ms</span></div>
            <div><strong>{summary.confidence_counts.high || 0}</strong><span>High confidence</span></div>
            <div><strong>{summary.confidence_counts.low || 0}</strong><span>Low confidence</span></div>
          </div>
        )}
      </div>
      <div className="card">
        <h2>Latest questions</h2>
        {!summary?.latest_questions?.length && <p className="muted">Ask questions to populate usage logs.</p>}
        <div className="citation-list">
          {summary?.latest_questions?.map((q, idx) => (
            <article key={idx} className="citation">
              <strong>{q.question}</strong>
              <span>Confidence: {q.confidence} · Citations: {q.citation_count} · {q.latency_ms} ms</span>
              <small>{new Date(q.created_at).toLocaleString()}</small>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
