import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import { AuthBar } from './components/AuthBar.jsx'
import { Upload } from './components/Upload.jsx'
import { Chat } from './components/Chat.jsx'
import { Documents } from './components/Documents.jsx'
import { Evaluation } from './components/Evaluation.jsx'
import { Analytics } from './components/Analytics.jsx'

function App() {
  const [tab, setTab] = useState('chat')

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Evidence-grounded RAG</p>
        <h1>TrustDoc AI</h1>
        <p>Enterprise-style document Q&A with citations, guardrails, evaluation, analytics, and document management.</p>
      </header>

      <AuthBar />

      <nav className="tabs">
        <button className={tab === 'chat' ? 'active' : ''} onClick={() => setTab('chat')}>Chat</button>
        <button className={tab === 'upload' ? 'active' : ''} onClick={() => setTab('upload')}>Upload</button>
        <button className={tab === 'documents' ? 'active' : ''} onClick={() => setTab('documents')}>Documents</button>
        <button className={tab === 'evaluation' ? 'active' : ''} onClick={() => setTab('evaluation')}>Evaluation</button>
        <button className={tab === 'analytics' ? 'active' : ''} onClick={() => setTab('analytics')}>Analytics</button>
      </nav>

      {tab === 'chat' && <Chat />}
      {tab === 'upload' && <Upload />}
      {tab === 'documents' && <Documents />}
      {tab === 'evaluation' && <Evaluation />}
      {tab === 'analytics' && <Analytics />}
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
