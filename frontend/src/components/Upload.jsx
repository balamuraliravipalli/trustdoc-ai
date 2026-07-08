import { useState } from 'react'
import api from '../api.js'

const commonTypes = ['HR', 'Security', 'Engineering', 'Finance', 'Legal', 'General']

export function Upload() {
  const [file, setFile] = useState(null)
  const [documentType, setDocumentType] = useState('HR')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleUpload(event) {
    event.preventDefault()
    if (!file) return setStatus('Choose a PDF first.')

    const form = new FormData()
    form.append('file', file)
    form.append('document_type', documentType.trim() || 'general')

    setLoading(true)
    setStatus('Uploading, chunking, embedding, and indexing in Qdrant...')
    try {
      const res = await api.post('/api/documents/upload', form)
      setStatus(`Indexed ${res.data.chunks} chunks from ${res.data.pages} pages as ${res.data.document_type}.`)
      setFile(null)
    } catch (err) {
      setStatus(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card narrow">
      <h2>Upload PDF</h2>
      <p className="muted">Add a policy, handbook, SOP, or project document. The backend extracts pages, chunks text, embeds it, and indexes it in Qdrant.</p>
      <form onSubmit={handleUpload} className="stack">
        <label>
          Document type label
          <input list="document-types" value={documentType} onChange={(e) => setDocumentType(e.target.value)} placeholder="HR, Security, Engineering" />
          <datalist id="document-types">
            {commonTypes.map((type) => <option key={type} value={type} />)}
          </datalist>
          <small className="muted">Use one clear label per uploaded file. The chat filter searches this label.</small>
        </label>
        <label>
          PDF file
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0])} />
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Indexing...' : 'Upload and index'}</button>
      </form>
      {status && <p className={status.includes('Indexed') ? 'status' : 'error'}>{status}</p>}
    </section>
  )
}
