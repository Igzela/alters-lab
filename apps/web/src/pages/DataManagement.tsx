import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { fetchJson, postJson } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
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
      <h2 className="text-lg font-semibold">{t('data.title')}</h2>
      <p className="text-gray-500 text-xs">
        {t('data.description')}
      </p>

      {error && <ErrorDisplay message={error} onRetry={loadManifest} />}
      {status && <p className="text-green-400 text-sm">{status}</p>}

      {loading && <LoadingSpinner label={t('data.loading')} />}

      {error && !manifest && !loading && (
        <ErrorDisplay message={error} onRetry={loadManifest} />
      )}

      {manifest && (
        <>
          <div className="mb-4">
            <button
              className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 disabled:opacity-50"
              onClick={exportAll}
              disabled={!!actionLoading}
            >
              {actionLoading === 'export' ? t('data.exporting') : t('data.exportAll')}
            </button>
          </div>

          <h3 className="text-sm font-medium mb-2">{t('data.recordCounts')}</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-2.5 mb-4">
            {manifest.runtime_areas.map(area => (
              <div key={area} className="p-2.5 bg-gray-800/30 rounded-lg border border-gray-700">
                <div className="flex justify-between items-center mb-1.5">
                  <strong className="text-sm">{area}</strong>
                  <span className="text-sm">{manifest.record_counts[area] ?? 0}</span>
                </div>
                <button
                  className="text-xs text-blue-400 hover:text-blue-300 disabled:opacity-50"
                  onClick={() => exportArea(area)}
                  disabled={!!actionLoading}
                >
                  {actionLoading === `export-${area}` ? t('data.exporting') : t('data.export')}
                </button>
              </div>
            ))}
          </div>

          <div className="p-2.5 bg-blue-950/30 rounded-lg border border-blue-800/30 text-xs text-gray-400 mb-4">
            <div>{t('data.longTermSave')} <strong>{manifest.default_long_term_save ? t('provider.yes') : t('provider.no')}</strong></div>
            <div>{t('data.exportSupported')} <strong>{manifest.export_supported ? t('provider.yes') : t('provider.no')}</strong></div>
            <div>{t('data.archiveSupported')} <strong>{manifest.archive_supported ? t('provider.yes') : t('provider.no')}</strong></div>
          </div>

          <div className="p-2.5 bg-amber-950/30 border border-amber-800/50 rounded-lg text-xs text-amber-200 mb-4">
            <strong>{t('data.archive')}</strong> {t('data.archiveDisabled')}
          </div>
        </>
      )}

      <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-700">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium">{t('data.deleteById')}</h4>
          <button className="text-xs text-gray-400 hover:text-white" onClick={() => setShowDeletePanel(!showDeletePanel)}>
            {showDeletePanel ? t('data.hide') : t('data.show')}
          </button>
        </div>
        {showDeletePanel && (
          <div>
            <p className="text-xs text-gray-400 mb-2">
              {t('data.deleteWarning')}
            </p>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <div>
                <label className="text-xs text-gray-400 block mb-0.5">{t('data.area')}</label>
                <input
                  className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                  value={deleteArea}
                  onChange={e => setDeleteArea(e.target.value)}
                  placeholder="e.g. weekly_reviews"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-0.5">{t('data.recordId')}</label>
                <input
                  className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                  value={deleteRecordId}
                  onChange={e => setDeleteRecordId(e.target.value)}
                  placeholder="e.g. review_2026-W01"
                />
              </div>
            </div>
            <div className="mb-2">
              <label className="text-xs text-gray-400 block mb-0.5">{t('data.typeDelete')}</label>
              <input
                className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                value={deleteConfirm}
                onChange={e => setDeleteConfirm(e.target.value)}
                placeholder="delete"
              />
            </div>
            <button
              className={`text-sm ${deleteArea && deleteRecordId && deleteConfirm === 'delete' && !actionLoading ? 'text-red-500 hover:text-red-400' : 'text-gray-500'}`}
              onClick={executeDelete}
              disabled={!deleteArea || !deleteRecordId || deleteConfirm !== 'delete' || !!actionLoading}
            >
              {actionLoading === 'delete' ? t('data.deleting') : t('data.deleteRecord')}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
