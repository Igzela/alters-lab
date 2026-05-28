import { useState } from 'react'
import { postJson } from '../api'

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
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Alter Dialogue</h2>
      <p className="text-gray-500 text-xs">Replies are not persisted unless explicitly saved. Provider output is not fact.</p>
      <select
        className="border border-gray-600 rounded px-3 py-2 text-sm bg-gray-800 text-white"
        value={alterId}
        onChange={e => setAlterId(e.target.value)}
      >
        {ALTERS.map(a => <option key={a} value={a}>{a}</option>)}
      </select>
      <div className="flex gap-2">
        <input
          className="flex-1 border border-gray-600 rounded px-3 py-2 text-sm bg-gray-800 text-white placeholder-gray-500"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type a message..."
        />
        <button
          className="px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          onClick={send}
          disabled={loading}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {reply && (
        <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-700">
          <strong className="text-sm">Reply:</strong>
          <p className="text-sm whitespace-pre-wrap mt-1">{reply}</p>
        </div>
      )}
    </div>
  )
}
