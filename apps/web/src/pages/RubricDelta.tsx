import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { postJson } from '../api'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import ErrorDisplay from '../components/ErrorDisplay'

export default function RubricDelta() {
  const { t } = useTranslation()
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await postJson('/rubric-delta/suggest', { caller: 'api' })
      setData(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('common.unknownError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('rubricDelta.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('rubricDelta.description')}</p>
      <Button variant="primary" accent="pink" onClick={generate} disabled={loading}>
        {loading ? t('common.generating') : t('rubricDelta.generate')}
      </Button>
      {error && <ErrorDisplay message={error} />}
      {data && (
        <Card accent="pink">
          <p className="text-sm">{t('rubricDelta.status')} {String(data.status)}</p>
          <pre className="text-xs mt-2 whitespace-pre-wrap overflow-auto max-h-[400px] p-3 rounded-lg font-mono" style={{ color: '#c4c2b8', backgroundColor: '#0e100f', border: '1px solid #242624' }}>
            {data.suggestions ? JSON.stringify(data.suggestions as Record<string, unknown>, null, 2) : ''}
          </pre>
        </Card>
      )}
    </div>
  )
}
