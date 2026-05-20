import { useState } from 'react'
import { fetchJson, postJson } from '../api'

const ALTERS = ['alter_A', 'alter_B', 'alter_C', 'alter_D']

export default function AlterDialogue() {
  const [alterId, setAlterId] = useState('alter_A')
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!message.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await postJson(`/provider-dialogue/${alterId}/reply`, {
        user_message: message,
        save_session: false,
      })
      setReply(res.reply_text)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Alter Dialogue</h2>
      <p style={{ color: '#888', fontSize: 12 }}>⚠ Replies are not persisted unless explicitly saved. Provider output is not fact.</p>
      <select value={alterId} onChange={e => setAlterId(e.target.value)} style={{ marginBottom: 8 }}>
        {ALTERS.map(a => <option key={a} value={a}>{a}</option>)}
      </select>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type a message..."
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={send} disabled={loading}>{loading ? '...' : 'Send'}</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {reply && (
        <div style={{ marginTop: 12, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <strong>Reply:</strong>
          <p style={{ whiteSpace: 'pre-wrap' }}>{reply}</p>
        </div>
      )}
    </div>
  )
}
