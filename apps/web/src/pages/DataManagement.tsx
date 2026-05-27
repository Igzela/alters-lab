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
    <div>
      <h2>Data Management</h2>
      <p style={{ color: '#888', fontSize: 12 }}>
        View, export, or delete your product data. All exports redact secrets. Deletion requires exact record id and explicit confirmation.
      </p>

      {error && <p style={{ color: '#b00020' }}>{error}</p>}
      {status && <p style={{ color: 'green' }}>{status}</p>}

      {manifest && (
        <>
          <div style={{ marginBottom: 16 }}>
            <button onClick={exportAll} style={{ marginRight: 8 }}>Export All Data</button>
          </div>

          <h3 style={{ margin: '0 0 10px' }}>Record Counts</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 10, marginBottom: 16 }}>
            {manifest.runtime_areas.map(area => (
              <div key={area} style={{ padding: 10, background: '#fafafa', borderRadius: 6, border: '1px solid #ddd' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <strong>{area}</strong>
                  <span style={{ fontSize: 14, color: '#333' }}>{manifest.record_counts[area] ?? 0}</span>
                </div>
                <button
                  onClick={() => exportArea(area)}
                  style={{ fontSize: 12, padding: '2px 8px' }}
                >
                  Export
                </button>
              </div>
            ))}
          </div>

          <div style={{ padding: 10, background: '#f6f8ff', borderRadius: 6, border: '1px solid #d0daf0', fontSize: 13, color: '#555', marginBottom: 16 }}>
            <div>Long-term save by default: <strong>{manifest.default_long_term_save ? 'Yes' : 'No'}</strong></div>
            <div>Export supported: <strong>{manifest.export_supported ? 'Yes' : 'No'}</strong></div>
            <div>Archive supported: <strong>{manifest.archive_supported ? 'Yes' : 'No'}</strong></div>
          </div>

          <div style={{ padding: 10, background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
            <strong>Archive:</strong> Archive requires exact record selection; disabled until record list/detail exists.
          </div>
        </>
      )}

      <div style={{ padding: 12, background: '#fafafa', borderRadius: 6, border: '1px solid #ddd', marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <h4 style={{ margin: 0 }}>Delete by Record ID</h4>
          <button onClick={() => setShowDeletePanel(!showDeletePanel)} style={{ fontSize: 12 }}>
            {showDeletePanel ? 'Hide' : 'Show'}
          </button>
        </div>
        {showDeletePanel && (
          <div>
            <p style={{ fontSize: 13, color: '#666', marginBottom: 8 }}>
              Use only when you know the exact local record id. Export first if unsure.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
              <div>
                <label style={{ fontSize: 12, display: 'block', marginBottom: 2 }}>Area</label>
                <input
                  value={deleteArea}
                  onChange={e => setDeleteArea(e.target.value)}
                  placeholder="e.g. weekly_reviews"
                  style={{ width: '100%', padding: 4, boxSizing: 'border-box' }}
                />
              </div>
              <div>
                <label style={{ fontSize: 12, display: 'block', marginBottom: 2 }}>Record ID</label>
                <input
                  value={deleteRecordId}
                  onChange={e => setDeleteRecordId(e.target.value)}
                  placeholder="e.g. review_2026-W01"
                  style={{ width: '100%', padding: 4, boxSizing: 'border-box' }}
                />
              </div>
            </div>
            <div style={{ marginBottom: 8 }}>
              <label style={{ fontSize: 12, display: 'block', marginBottom: 2 }}>Type <strong>delete</strong> to confirm</label>
              <input
                value={deleteConfirm}
                onChange={e => setDeleteConfirm(e.target.value)}
                placeholder="delete"
                style={{ width: '100%', padding: 4, boxSizing: 'border-box' }}
              />
            </div>
            <button
              onClick={executeDelete}
              disabled={!deleteArea || !deleteRecordId || deleteConfirm !== 'delete'}
              style={{
                color: deleteArea && deleteRecordId && deleteConfirm === 'delete' ? '#b00020' : '#888',
              }}
            >
              Delete Record
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
