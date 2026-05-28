import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { postJson } from '../api'
import { fadeIn } from '../animations'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Select } from '../components/Input'
import { Banner } from '../components/Banner'

const ALTERS = [
  { id: 'alter_A', label: 'Alter A' },
  { id: 'alter_B', label: 'Alter B' },
  { id: 'alter_C', label: 'Alter C' },
  { id: 'alter_D', label: 'Alter D' },
]

export default function AlterDialogue() {
  const { t } = useTranslation()
  const [alterId, setAlterId] = useState('alter_A')
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const replyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (reply && replyRef.current) {
      fadeIn(replyRef.current)
    }
  }, [reply])

  const send = async () => {
    if (!message.trim()) return
    setLoading(true)
    setError('')
    setReply('')
    try {
      const res = await postJson(`/provider-dialogue/${alterId}/reply`, {
        user_message: message,
        save_session: false,
      })
      setReply(res.reply_text)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('dialogue.unknownError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('dialogue.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('dialogue.description')}</p>
      <Select value={alterId} onChange={e => setAlterId(e.target.value)}>
        {ALTERS.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
      </Select>
      <div className="flex gap-2">
        <Input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={t('dialogue.placeholder')}
          className="flex-1"
        />
        <Button variant="primary" accent="blue" onClick={send} disabled={loading}>
          {loading ? t('common.sending') : t('dialogue.send')}
        </Button>
      </div>
      {error && <Banner variant="error">{error}</Banner>}
      {reply && (
        <div ref={replyRef}>
          <Card accent="blue">
            <strong className="text-sm">{t('dialogue.reply')}</strong>
            <p className="text-sm whitespace-pre-wrap mt-1" style={{ color: '#c4c2b8' }}>{reply}</p>
          </Card>
        </div>
      )}
    </div>
  )
}
