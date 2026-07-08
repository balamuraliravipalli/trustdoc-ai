import { useEffect, useState } from 'react'
import api from '../api.js'

export function Documents() {
  const [docs, setDocs] = useState([])
  const [selected, setSelected] = useState(null)
  const [chunks, setChunks] = useState([])
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  async function loadDocs() {
    try {
      const res = await api.get('/api/documents')
      setDocs(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  async function loadChunks(doc) {
    setSelected(doc)
    setChunks([])
    try {
      const res = await api.get(`/api/documents/${doc.id}/chunks`)
      setChunks(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  async function deleteDoc(doc) {
    if (!confirm(`Delete ${doc.filename}? This removes DB records and Qdrant vectors.`)) return
    setStatus('Deleting document and vectors...')
    try {
      await api.delete(`/api/documents/${doc.id}`)
      setStatus('Deleted document successfully.')
      setSelected(null)
      setChunks([])
      await loadDocs()
    } catch (err) {
      setStatus(err.response?.data?.detail || err.message)
    }
  }

  useEffect(() => { loadDocs() }, [])

  return (
    <section className="grid-two">
      <div className="card">
        <div className="space-between">
          <h2>Documents</h2>
          <button onClick={loadDocs}>Refresh</button>
        </div>
        <p className="muted">Manage uploaded PDFs and inspect chunks used for retrieval.</p>
        {error && <p className="error">{error}</p>}
        {status && <p className={status.includes('success') || status.includes('Deleted') ? 'status' : 'muted'}>{status}</p>}
        <div className="doc-list">
          {docs.map((doc) => (
            <article key={doc.id} className="doc-card">
              <strong>{doc.filename}</strong>
              <span>{doc.document_type}</span>
              <span>{doc.page_count} pages · {doc.chunk_count} chunks</span>
              <small>{new Date(doc.created_at).toLocaleString()}</small>
              <div className="button-row">
                <button className="ghost" onClick={() => loadChunks(doc)}>View chunks</button>
                <button className="danger" onClick={() => deleteDoc(doc)}>Delete</button>
              </div>
            </article>
          ))}
        </div>
      </div>
      <div className="card">
        <h2>Chunk preview</h2>
        {!selected && <p className="muted">Select a document to preview page-aware chunks.</p>}
        {selected && <p className="muted">{selected.filename} · {chunks.length} chunks</p>}
        <div className="citation-list">
          {chunks.map((chunk) => (
            <article key={chunk.id} className="citation">
              <strong>Page {chunk.page} · Chunk {chunk.chunk_index}</strong>
              <span>{chunk.token_estimate} estimated tokens</span>
              <p>{chunk.text_preview}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
