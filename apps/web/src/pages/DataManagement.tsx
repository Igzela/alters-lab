import { useState, useEffect } from 'react'
import { fetchJson, postJson } from '../api'

interface Manifest {
  runtime_areas: string[]
  record_counts: Record<string, number>
  default_long_term_save: boolean
  manual_delete_supported: boolean
  export_supported: boolean
  archive_supported: boolean
}

export default function DataManagement() {
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [showDeletePanel, setShowDeletePanel] = useState(false)
  const [deleteArea, setDeleteArea] = useState('')
  const [deleteRecordId, setDeleteRecordId] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState('')

  useEffect(() => {
    fetchJson('/p6-data-retention/manifest')
      .then(setManifest)
      .catch(e => setError(e instanceof Error ? e.message : 'Unable to load manifest'))
  }, [])

  const exportAll = async () => {
    setError('')
    setStatus('')
    try {
      const res = await postJson('/p6-data-retention/export', { areas: [], caller: 'api' })
      setStatus(`Exported to: ${res.path || 'unknown path'}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Export failed')
    }
  }

  const exportArea = async (area: string) => {
    setError('')
    setStatus('')
    try {
      const res = await postJson('/p6-data-retention/export', { areas: [area], caller: 'api' })
      setStatus(`Exported ${area} to: ${res.path || 'unknown path'}`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Export failed')
    }
  }

  const executeDelete = async () => {
    if (!deleteArea || !deleteRecordId || deleteConfirm !== 'delete') return
    setError('')
    setStatus('')
    try {
      await postJson('/p6-data-retention/delete', {
        record: { area: deleteArea, record_id: deleteRecordId },
        confirmation: 'delete',
        caller: 'api',
      })
      setStatus(`Deleted: ${deleteArea}/${deleteRecordId}`)
      setShowDeletePanel(false)
      setDeleteArea('')
      setDeleteRecordId('')
      setDeleteConfirm('')
      fetchJson('/p6-data-retention/manifest').then(setManifest).catch(() => {})
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Delete failed')
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Data Management</h2>
      <p className="text-gray-500 text-xs">
        View, export, or delete your product data. All exports redact secrets. Deletion requires exact record id and explicit confirmation.
      </p>

      {error && <p className="text-red-500 text-sm">{error}</p>}
      {status && <p className="text-green-400 text-sm">{status}</p>}

      {manifest && (
        <>
          <div className="mb-4">
            <button className="px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700" onClick={exportAll}>Export All Data</button>
          </div>

          <h3 className="text-sm font-medium mb-2">Record Counts</h3>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-2.5 mb-4">
            {manifest.runtime_areas.map(area => (
              <div key={area} className="p-2.5 bg-gray-800/30 rounded-lg border border-gray-700">
                <div className="flex justify-between items-center mb-1.5">
                  <strong className="text-sm">{area}</strong>
                  <span className="text-sm">{manifest.record_counts[area] ?? 0}</span>
                </div>
                <button className="text-xs text-blue-400 hover:text-blue-300" onClick={() => exportArea(area)}>Export</button>
              </div>
            ))}
          </div>

          <div className="p-2.5 bg-blue-950/30 rounded-lg border border-blue-800/30 text-xs text-gray-400 mb-4">
            <div>Long-term save by default: <strong>{manifest.default_long_term_save ? 'Yes' : 'No'}</strong></div>
            <div>Export supported: <strong>{manifest.export_supported ? 'Yes' : 'No'}</strong></div>
            <div>Archive supported: <strong>{manifest.archive_supported ? 'Yes' : 'No'}</strong></div>
          </div>

          <div className="p-2.5 bg-amber-950/30 border border-amber-800/50 rounded-lg text-xs text-amber-200 mb-4">
            <strong>Archive:</strong> Archive requires exact record selection; disabled until record list/detail exists.
          </div>
        </>
      )}

      <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-700">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium">Delete by Record ID</h4>
          <button className="text-xs text-gray-400 hover:text-white" onClick={() => setShowDeletePanel(!showDeletePanel)}>
            {showDeletePanel ? 'Hide' : 'Show'}
          </button>
        </div>
        {showDeletePanel && (
          <div>
            <p className="text-xs text-gray-400 mb-2">
              Use only when you know the exact local record id. Export first if unsure.
            </p>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <div>
                <label className="text-xs text-gray-400 block mb-0.5">Area</label>
                <input
                  className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                  value={deleteArea}
                  onChange={e => setDeleteArea(e.target.value)}
                  placeholder="e.g. weekly_reviews"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-0.5">Record ID</label>
                <input
                  className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                  value={deleteRecordId}
                  onChange={e => setDeleteRecordId(e.target.value)}
                  placeholder="e.g. review_2026-W01"
                />
              </div>
            </div>
            <div className="mb-2">
              <label className="text-xs text-gray-400 block mb-0.5">Type <strong>delete</strong> to confirm</label>
              <input
                className="w-full px-2 py-1 text-sm border border-gray-600 rounded bg-gray-800 text-white"
                value={deleteConfirm}
                onChange={e => setDeleteConfirm(e.target.value)}
                placeholder="delete"
              />
            </div>
            <button
              className={`text-sm ${deleteArea && deleteRecordId && deleteConfirm === 'delete' ? 'text-red-500 hover:text-red-400' : 'text-gray-500'}`}
              onClick={executeDelete}
              disabled={!deleteArea || !deleteRecordId || deleteConfirm !== 'delete'}
            >
              Delete Record
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
