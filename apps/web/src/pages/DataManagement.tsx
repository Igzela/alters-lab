import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, postJson } from '../api'
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
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [actionLoading, setActionLoading] = useState('')
  const [showDeletePanel, setShowDeletePanel] = useState(false)
  const [deleteArea, setDeleteArea] = useState('')
  const [deleteRecordId, setDeleteRecordId] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState('')

  const loadManifest = useCallback(() => {
    setLoading(true)
    setError('')
    fetchJson('/p6-data-retention/manifest')
      .then(setManifest)
      .catch(e => setError(e instanceof Error ? e.message : t('data.unableToLoad')))
      .finally(() => setLoading(false))
  }, [t])

  useEffect(() => { loadManifest() }, [loadManifest])

  const exportAll = async () => {
    setError('')
    setStatus('')
    setActionLoading('export')
    try {
      const res = await postJson('/p6-data-retention/export', { areas: [], caller: 'api' })
      setStatus(`${t('data.exportedTo')} ${res.path || 'unknown path'}`)
      toast({ title: t('data.exported'), variant: 'success' })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('data.exportFailed'))
    } finally {
      setActionLoading('')
    }
  }

  const exportArea = async (area: string) => {
    setError('')
    setStatus('')
    setActionLoading(`export-${area}`)
    try {
      const res = await postJson('/p6-data-retention/export', { areas: [area], caller: 'api' })
      setStatus(`${t('data.exported')} ${area} ${t('data.exportedTo')} ${res.path || 'unknown path'}`)
      toast({ title: `${t('data.exported')} ${area}`, variant: 'success' })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('data.exportFailed'))
    } finally {
      setActionLoading('')
    }
  }

  const executeDelete = async () => {
    if (!deleteArea || !deleteRecordId || deleteConfirm !== 'delete') return
    setError('')
    setStatus('')
    setActionLoading('delete')
    try {
      await postJson('/p6-data-retention/delete', {
        record: { area: deleteArea, record_id: deleteRecordId },
        confirmation: 'delete',
        caller: 'api',
      })
      setStatus(`${t('data.deleted')} ${deleteArea}/${deleteRecordId}`)
      toast({ title: `${t('data.deleted')} ${deleteArea}/${deleteRecordId}`, variant: 'success' })
      setShowDeletePanel(false)
      setDeleteArea('')
      setDeleteRecordId('')
      setDeleteConfirm('')
      loadManifest()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t('data.deleteFailed'))
    } finally {
      setActionLoading('')
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold tracking-tight" style={{ letterSpacing: '-0.02em' }}>{t('data.title')}</h2>
      <p className="text-sm" style={{ color: '#7c7c6f' }}>{t('data.description')}</p>

      {error && <ErrorDisplay message={error} onRetry={loadManifest} />}
      {status && <Banner variant="success">{status}</Banner>}

      {loading && <Skeleton lines={5} />}

      {!manifest && !loading && error && (
        <ErrorDisplay message={error} onRetry={loadManifest} />
      )}

      {manifest && (
        <>
          <div className="mb-4">
            <Button variant="primary" onClick={exportAll} disabled={!!actionLoading}>
              {actionLoading === 'export' ? t('data.exporting') : t('data.exportAll')}
            </Button>
          </div>

          <h3 className="text-sm font-medium mb-2">{t('data.recordCounts')}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-2.5 mb-4">
            {manifest.runtime_areas.map(area => (
              <Card key={area}>
                <div className="flex justify-between items-center mb-1.5">
                  <strong className="text-sm">{area}</strong>
                  <span className="text-sm" style={{ color: '#c4c2b8' }}>{manifest.record_counts[area] ?? 0}</span>
                </div>
                <Button variant="ghost" onClick={() => exportArea(area)} disabled={!!actionLoading}>
                  {actionLoading === `export-${area}` ? t('data.exporting') : t('data.export')}
                </Button>
              </Card>
            ))}
          </div>

          <Card>
            <div className="text-xs space-y-1" style={{ color: '#7c7c6f' }}>
              <div>{t('data.longTermSave')} <strong style={{ color: '#c4c2b8' }}>{manifest.default_long_term_save ? t('provider.yes') : t('provider.no')}</strong></div>
              <div>{t('data.exportSupported')} <strong style={{ color: '#c4c2b8' }}>{manifest.export_supported ? t('provider.yes') : t('provider.no')}</strong></div>
              <div>{t('data.archiveSupported')} <strong style={{ color: '#c4c2b8' }}>{manifest.archive_supported ? t('provider.yes') : t('provider.no')}</strong></div>
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
            <p className="text-xs mb-3" style={{ color: '#7c7c6f' }}>
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
              disabled={!deleteArea || !deleteRecordId || deleteConfirm !== 'delete' || !!actionLoading}
            >
              {actionLoading === 'delete' ? t('data.deleting') : t('data.deleteRecord')}
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
