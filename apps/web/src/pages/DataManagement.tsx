import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useDataManifest, useExportData, useDeleteData } from '../hooks/useApi'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Field } from '../components/Input'
import { Banner } from '../components/Banner'
import { Skeleton } from '../components/Skeleton'
import { useToast } from '../components/Toast'
import ErrorDisplay from '../components/ErrorDisplay'

interface Manifest {
  runtime_areas: string[]
  record_counts: Record<string, number>
  default_long_term_save: boolean
  manual_delete_supported: boolean
  export_supported: boolean
  archive_supported: boolean
}

export default function DataManagement() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const manifestQuery = useDataManifest()
  const exportMutation = useExportData()
  const deleteMutation = useDeleteData()

  const [status, setStatus] = useState('')
  const [showDeletePanel, setShowDeletePanel] = useState(false)
  const [deleteArea, setDeleteArea] = useState('')
  const [deleteRecordId, setDeleteRecordId] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState('')

  const manifest = manifestQuery.data as Manifest | undefined

  const exportAll = () => {
    setStatus('')
    exportMutation.mutate(
      { areas: [], caller: 'api' },
      {
        onSuccess: (res) => {
          setStatus(`${t('data.exportedTo')} ${(res as Record<string, unknown>).path || 'unknown path'}`)
          toast({ title: t('data.exported'), variant: 'success' })
        },
      }
    )
  }

  const exportArea = (area: string) => {
    setStatus('')
    exportMutation.mutate(
      { areas: [area], caller: 'api' },
      {
        onSuccess: (res) => {
          setStatus(`${t('data.exported')} ${area} ${t('data.exportedTo')} ${(res as Record<string, unknown>).path || 'unknown path'}`)
          toast({ title: `${t('data.exported')} ${area}`, variant: 'success' })
        },
      }
    )
  }

  const executeDelete = () => {
    if (!deleteArea || !deleteRecordId || deleteConfirm !== 'delete') return
    setStatus('')
    deleteMutation.mutate(
      {
        record: { area: deleteArea, record_id: deleteRecordId },
        confirmation: 'delete',
        caller: 'api',
      },
      {
        onSuccess: () => {
          setStatus(`${t('data.deleted')} ${deleteArea}/${deleteRecordId}`)
          toast({ title: `${t('data.deleted')} ${deleteArea}/${deleteRecordId}`, variant: 'success' })
          setShowDeletePanel(false)
          setDeleteArea('')
          setDeleteRecordId('')
          setDeleteConfirm('')
        },
      }
    )
  }

  const error = manifestQuery.error || exportMutation.error || deleteMutation.error

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight">{t('data.title')}</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{t('data.description')}</p>

      {error && <ErrorDisplay message={(error as Error).message} onRetry={() => manifestQuery.refetch()} />}
      {status && <Banner variant="success">{status}</Banner>}

      {manifestQuery.isLoading && <Skeleton lines={5} />}

      {manifest && (
        <>
          <div className="mb-4">
            <Button variant="primary" onClick={exportAll} disabled={exportMutation.isPending}>
              {exportMutation.isPending ? t('data.exporting') : t('data.exportAll')}
            </Button>
          </div>

          <h3 className="text-sm font-medium mb-2">{t('data.recordCounts')}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-2.5 mb-4">
            {manifest.runtime_areas.map(area => (
              <Card key={area}>
                <div className="flex justify-between items-center mb-1.5">
                  <strong className="text-sm">{area}</strong>
                  <span className="text-sm font-mono" style={{ color: 'var(--color-text-secondary)' }}>{manifest.record_counts[area] ?? 0}</span>
                </div>
                <Button variant="ghost" onClick={() => exportArea(area)} disabled={exportMutation.isPending}>
                  {exportMutation.isPending ? t('data.exporting') : t('data.export')}
                </Button>
              </Card>
            ))}
          </div>

          <Card>
            <div className="text-xs space-y-1" style={{ color: 'var(--color-text-muted)' }}>
              <div>{t('data.longTermSave')} <strong style={{ color: 'var(--color-text-secondary)' }}>{manifest.default_long_term_save ? t('provider.yes') : t('provider.no')}</strong></div>
              <div>{t('data.exportSupported')} <strong style={{ color: 'var(--color-text-secondary)' }}>{manifest.export_supported ? t('provider.yes') : t('provider.no')}</strong></div>
              <div>{t('data.archiveSupported')} <strong style={{ color: 'var(--color-text-secondary)' }}>{manifest.archive_supported ? t('provider.yes') : t('provider.no')}</strong></div>
            </div>
          </Card>

          <Banner variant="warning">
            <strong>{t('data.archive')}</strong> {t('data.archiveDisabled')}
          </Banner>
        </>
      )}

      <Card>
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium">{t('data.deleteById')}</h4>
          <Button variant="ghost" onClick={() => setShowDeletePanel(!showDeletePanel)}>
            {showDeletePanel ? t('data.hide') : t('data.show')}
          </Button>
        </div>
        {showDeletePanel && (
          <div>
            <p className="text-xs mb-3" style={{ color: 'var(--color-text-muted)' }}>
              {t('data.deleteWarning')}
            </p>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <Field label={t('data.area')}>
                <Input value={deleteArea} onChange={e => setDeleteArea(e.target.value)} placeholder="e.g. weekly_reviews" />
              </Field>
              <Field label={t('data.recordId')}>
                <Input value={deleteRecordId} onChange={e => setDeleteRecordId(e.target.value)} placeholder="e.g. review_2026-W01" />
              </Field>
            </div>
            <Field label={t('data.typeDelete')}>
              <Input value={deleteConfirm} onChange={e => setDeleteConfirm(e.target.value)} placeholder="delete" />
            </Field>
            <Button
              variant="danger"
              onClick={executeDelete}
              disabled={!deleteArea || !deleteRecordId || deleteConfirm !== 'delete' || deleteMutation.isPending}
            >
              {deleteMutation.isPending ? t('data.deleting') : t('data.deleteRecord')}
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
