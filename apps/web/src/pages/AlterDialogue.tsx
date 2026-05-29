import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useAlterReply } from '../hooks/useApi'
import { fadeIn } from '../animations'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Select } from '../components/Input'
import { Banner } from '../components/Banner'

const ALTERS = ['alter_A', 'alter_B', 'alter_C', 'alter_D']
const ALTER_LABELS: Record<string, string> = {
  alter_A: 'common.alterA',
  alter_B: 'common.alterB',
  alter_C: 'common.alterC',
  alter_D: 'common.alterD',
}

export default function AlterDialogue() {
  const { t } = useTranslation()
  const [alterId, setAlterId] = useState('alter_A')
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const replyRef = useRef<HTMLDivElement>(null)
  const mutation = useAlterReply()

  useEffect(() => {
    if (reply && replyRef.current) {
      fadeIn(replyRef.current)
    }
  }, [reply])

  const send = () => {
    if (!message.trim()) return
    setReply('')
    mutation.mutate(
      { alterId, message },
      {
        onSuccess: (res) => {
          setReply((res as Record<string, unknown>).reply_text as string)
        },
      }
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('dialogue.title')}</h2>
      <p className="text-sm" style={{ color: '#78716c' }}>{t('dialogue.description')}</p>
      <Select value={alterId} onChange={e => setAlterId(e.target.value)}>
        {ALTERS.map(a => <option key={a} value={a}>{t(ALTER_LABELS[a])}</option>)}
      </Select>
      <div className="flex gap-2">
        <Input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={t('dialogue.placeholder')}
          className="flex-1"
        />
        <Button variant="primary" onClick={send} disabled={mutation.isPending}>
          {mutation.isPending ? t('common.sending') : t('dialogue.send')}
        </Button>
      </div>
      {mutation.error && <Banner variant="error">{(mutation.error as Error).message}</Banner>}
      {reply && (
        <div ref={replyRef}>
          <Card accent="amber">
            <strong className="text-sm">{t('dialogue.reply')}</strong>
            <p className="text-sm whitespace-pre-wrap mt-1" style={{ color: '#78716c' }}>{reply}</p>
          </Card>
        </div>
      )}
    </div>
  )
}
