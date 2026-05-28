import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { postJson } from '../api'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import ErrorDisplay from '../components/ErrorDisplay'

export default function CheckpointPlan() {
  const { t } = useTranslation()
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await postJson('/checkpoint-regeneration/plan', { caller: 'api' })
      setData(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('common.unknownError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('checkpointPlan.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('checkpointPlan.description')}</p>
      <Button variant="primary" onClick={generate} disabled={loading}>
        {loading ? t('common.generating') : t('checkpointPlan.generate')}
      </Button>
      {error && <ErrorDisplay message={error} />}
      {data && (
        <Card>
          <p className="text-sm">{t('checkpointPlan.status')} {String(data.status)}</p>
          <pre className="text-xs mt-2 whitespace-pre-wrap" style={{ color: '#c4c2b8' }}>
            {data.plan ? JSON.stringify(data.plan as Record<string, unknown>, null, 2) : ''}
          </pre>
        </Card>
      )}
    </div>
  )
}
