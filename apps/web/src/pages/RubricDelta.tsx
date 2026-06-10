import { useTranslation } from 'react-i18next'
import { useSuggestRubricDelta } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import ErrorDisplay from '../components/ErrorDisplay'

export default function RubricDelta() {
  const { t } = useTranslation()
  const mutation = useSuggestRubricDelta()

  const generate = () => mutation.mutate({ caller: 'api' })

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('rubricDelta.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('rubricDelta.description')}</p>
      <Button variant="primary" onClick={generate} disabled={mutation.isPending}>
        {mutation.isPending ? t('common.generating') : t('rubricDelta.generate')}
      </Button>
      {mutation.error && <ErrorDisplay message={(mutation.error as Error).message} />}
      {mutation.data && (() => {
        const data = mutation.data as { status: string; suggestions?: Record<string, { current_weight: number; suggested_weight: number; rationale: string }> }
        const suggestions = data.suggestions ?? {}
        const dims = Object.entries(suggestions)

        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge variant="success">{data.status}</Badge>
            </div>

            {dims.length === 0 && (
              <Card>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('rubricDelta.noSuggestions')}</p>
              </Card>
            )}

            {dims.map(([name, s]) => {
              const diff = s.suggested_weight - s.current_weight
              const arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→'
              const arrowColor = diff > 0 ? 'var(--color-success)' : diff < 0 ? 'var(--color-error)' : 'var(--color-text-secondary)'

              return (
                <Card key={name} accent="amber">
                  <h3 className="text-sm font-semibold mb-2">{name}</h3>
                  <div className="flex items-center gap-3 text-sm mb-2">
                    <span style={{ color: 'var(--color-text-secondary)' }}>{t('rubricDelta.currentWeight')}:</span>
                    <span className="font-mono">{s.current_weight}</span>
                    <span style={{ color: arrowColor, fontSize: '1.1em' }}>{arrow}</span>
                    <span style={{ color: 'var(--color-text-secondary)' }}>{t('rubricDelta.suggestedWeight')}:</span>
                    <span className="font-mono font-semibold">{s.suggested_weight}</span>
                    <Badge variant={diff > 0 ? 'success' : diff < 0 ? 'error' : 'muted'}>
                      {diff > 0 ? '+' : ''}{diff}
                    </Badge>
                  </div>
                  <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{s.rationale}</p>
                </Card>
              )
            })}
          </div>
        )
      })()}
    </div>
  )
}
