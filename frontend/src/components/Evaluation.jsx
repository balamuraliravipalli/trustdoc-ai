import { useState } from 'react'
import api from '../api.js'

const defaultCases = JSON.stringify({
  cases: [
    {
      question: 'What is the remote work policy?',
      expected_file_contains: 'hr_policy',
      expected_page: 1,
      expected_answer_contains: 'two days'
    },
    {
      question: 'What is the password length requirement?',
      expected_file_contains: 'security_policy',
      expected_page: 1,
      expected_answer_contains: '12 characters'
    },
    {
      question: 'What should engineers do before deploying code?',
      expected_file_contains: 'engineering_sop',
      expected_page: 1,
      expected_answer_contains: 'pull request'
    },
    {
      question: 'What is the company car policy?',
      expected_file_contains: '',
      expected_page: null,
      expected_answer_contains: 'could not find',
      should_refuse: true
    }
  ]
}, null, 2)

export function Evaluation() {
  const [payload, setPayload] = useState(defaultCases)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function runEval() {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await api.post('/api/evaluation/run', JSON.parse(payload))
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="grid-two">
      <div className="card">
        <h2>Evaluation cases</h2>
        <p className="muted">Run a mini regression suite to check retrieval, citations, refusal behavior, answer quality, and latency.</p>
        <textarea rows="20" value={payload} onChange={(e) => setPayload(e.target.value)} />
        <button onClick={runEval} disabled={loading}>{loading ? 'Running...' : 'Run evaluation'}</button>
        {error && <p className="error">{error}</p>}
      </div>
      <div className="card">
        <h2>Results</h2>
        {!result && <p className="muted">Upload the three sample PDFs, then run evaluation.</p>}
        {result && (
          <div>
            <div className="metric-grid wide">
              <div><strong>{result.total_cases}</strong><span>Cases</span></div>
              <div><strong>{result.citation_accuracy}</strong><span>Citation accuracy</span></div>
              <div><strong>{result.answer_contains_accuracy}</strong><span>Answer match</span></div>
              <div><strong>{result.refusal_accuracy ?? '—'}</strong><span>Refusal accuracy</span></div>
              <div><strong>{result.average_latency_ms}</strong><span>Avg latency ms</span></div>
            </div>
            <div className="citation-list">
              {result.results.map((r, idx) => (
                <article key={idx} className="citation">
                  <strong>{r.question}</strong>
                  <span>Citation: {String(r.citation_hit)} · Answer: {String(r.answer_contains_hit)} · Refusal: {r.refusal_hit === null ? 'n/a' : String(r.refusal_hit)} · Confidence: {r.confidence} · {r.latency_ms} ms</span>
                  <p>{r.answer}</p>
                </article>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
