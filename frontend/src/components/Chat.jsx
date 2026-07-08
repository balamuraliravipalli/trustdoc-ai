import { useState } from 'react'
import api from '../api.js'

const exampleQuestions = [
  'What is the remote work policy?',
  'What is the password requirement?',
  'What should engineers do before deploying code?',
  'What is the company car policy?'
]

export function Chat() {
  const [question, setQuestion] = useState('What is the remote work policy?')
  const [documentType, setDocumentType] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function ask(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const payload = { question }
      if (documentType.trim()) payload.document_type = documentType.trim()
      const res = await api.post('/api/chat/ask', payload)
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
        <h2>Ask documents</h2>
        <p className="muted small-top">Search all uploaded documents, or filter to a document type you used during upload.</p>
        <form onSubmit={ask} className="stack">
          <label>
            Optional uploaded document type filter
            <input
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              placeholder="Leave blank to search all documents"
            />
            <small className="muted">Examples: HR, Security, Engineering. This filters by the label chosen during upload.</small>
          </label>
          <label>
            Question
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows="5" />
          </label>
          <button disabled={loading || !question.trim()}>{loading ? 'Thinking...' : 'Ask'}</button>
        </form>
        <div className="quick-actions">
          {exampleQuestions.map((q) => (
            <button key={q} type="button" className="ghost" onClick={() => setQuestion(q)}>{q}</button>
          ))}
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="card">
        <h2>Answer</h2>
        {!result && <p className="muted">Upload PDFs, then ask a document-grounded question.</p>}
        {result && (
          <div>
            <div className="meta-row">
              <span>Confidence: <strong className={`badge ${result.confidence}`}>{result.confidence}</strong></span>
              <span>{result.latency_ms} ms</span>
            </div>
            <div className="answer">{result.answer}</div>
            <h3>Citations</h3>
            {result.citations.length === 0 && <p className="muted">No citations displayed because the system did not find support in the uploaded documents.</p>}
            <div className="citation-list">
              {result.citations.map((c) => (
                <article key={c.chunk_id} className="citation">
                  <strong>[{c.index}] {c.file}</strong>
                  <span>Page {c.page} · retrieval score {c.score}</span>
                  <p>{c.text_preview}</p>
                </article>
              ))}
            </div>
            <details>
              <summary>Retrieval debug</summary>
              <pre>{JSON.stringify(result.retrieval_debug, null, 2)}</pre>
            </details>
          </div>
        )}
      </div>
    </section>
  )
}
