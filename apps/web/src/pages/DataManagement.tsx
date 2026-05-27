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

interface ActionResult {
  status: string
  path: string | null
}

export default function DataManagement() {
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<{ area: string; record_id: string } | null>(null)
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

  const confirmDelete = (area: string, record_id: string) => {
    setDeleteTarget({ area, record_id })
    setDeleteConfirm('')
  }

  const executeDelete = async () => {
    if (!deleteTarget || deleteConfirm !== 'delete') return
    setError('')
    setStatus('')
    try {
      await postJson('/p6-data-retention/delete', {
        record: deleteTarget,
        confirmation: 'delete',
        caller: 'api',
      })
      setStatus(`Deleted: ${deleteTarget.area}/${deleteTarget.record_id}`)
      setDeleteTarget(null)
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
        View, export, archive, or delete your product data. All exports redact secrets. Deletion requires explicit confirmation.
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
                <div style={{ display: 'flex', gap: 6 }}>
                  <button
                    onClick={() => exportArea(area)}
                    style={{ fontSize: 12, padding: '2px 8px' }}
                  >
                    Export
                  </button>
                  {(manifest.record_counts[area] ?? 0) > 0 && manifest.manual_delete_supported && (
                    <button
                      onClick={() => confirmDelete(area, `last_${area}`)}
                      style={{ fontSize: 12, padding: '2px 8px', color: '#b00020' }}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div style={{ padding: 10, background: '#f6f8ff', borderRadius: 6, border: '1px solid #d0daf0', fontSize: 13, color: '#555' }}>
            <div>Long-term save by default: <strong>{manifest.default_long_term_save ? 'Yes' : 'No'}</strong></div>
            <div>Export supported: <strong>{manifest.export_supported ? 'Yes' : 'No'}</strong></div>
            <div>Archive supported: <strong>{manifest.archive_supported ? 'Yes' : 'No'}</strong></div>
          </div>
        </>
      )}

      {deleteTarget && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', padding: 20, borderRadius: 8, border: '1px solid #ddd', maxWidth: 400, width: '100%' }}>
            <h3 style={{ margin: '0 0 10px', color: '#b00020' }}>Confirm Deletion</h3>
            <p style={{ fontSize: 14, marginBottom: 10 }}>
              Delete <strong>{deleteTarget.area}/{deleteTarget.record_id}</strong>?
              This cannot be undone.
            </p>
            <p style={{ fontSize: 13, marginBottom: 10 }}>
              Type <strong>delete</strong> to confirm:
            </p>
            <input
              value={deleteConfirm}
              onChange={e => setDeleteConfirm(e.target.value)}
              placeholder="delete"
              style={{ width: '100%', padding: 6, marginBottom: 10, boxSizing: 'border-box' }}
            />
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={executeDelete}
                disabled={deleteConfirm !== 'delete'}
                style={{ color: deleteConfirm === 'delete' ? '#b00020' : '#888' }}
              >
                Delete
              </button>
              <button onClick={() => { setDeleteTarget(null); setDeleteConfirm('') }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
