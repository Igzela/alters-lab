type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started'

export default function GettingStarted({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const sectionStyle = {
    marginBottom: 24,
    padding: 16,
    border: '1px solid #333',
    borderRadius: 8,
  }
  const h2Style = { fontSize: 16, marginTop: 0, marginBottom: 8 }
  const pStyle = { color: '#aaa', fontSize: 14, lineHeight: '1.5', margin: 0 }
  const btnStyle = {
    padding: '6px 12px',
    background: '#333',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    fontSize: 13,
    marginTop: 8,
  }

  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Getting Started</h2>

      <div style={sectionStyle}>
        <h3 style={h2Style}>1. Provider is disabled by default</h3>
        <p style={pStyle}>
          Alters Lab starts with provider mode <strong>disabled</strong>. No LLM calls, no API key needed.
          Switch to <strong>mock</strong> mode in Provider Settings to test dialogue features without network calls.
        </p>
        <button style={btnStyle} onClick={() => onNavigate('provider')}>
          Open Provider Settings
        </button>
      </div>

      <div style={sectionStyle}>
        <h3 style={h2Style}>2. Run your first Weekly Review</h3>
        <p style={pStyle}>
          Paste a weekly note, review extracted records, score your action alignment.
          Each review creates calibration data that tracks your patterns over time.
        </p>
        <button style={btnStyle} onClick={() => onNavigate('weekly')}>
          Start Weekly Review
        </button>
      </div>

      <div style={sectionStyle}>
        <h3 style={h2Style}>3. Check system health</h3>
        <p style={pStyle}>
          Run <code>alters-lab doctor</code> in your terminal to verify installation, config, data directories, and provider mode.
        </p>
      </div>

      <div style={sectionStyle}>
        <h3 style={h2Style}>4. Back up before risky changes</h3>
        <p style={pStyle}>
          Run <code>alters-lab backup</code> to create a snapshot of your data.
          User data persists across restarts and is not removed on uninstall.
        </p>
      </div>

      <div style={{ ...sectionStyle, borderColor: '#555' }}>
        <h3 style={h2Style}>Boundaries</h3>
        <p style={pStyle}>
          <strong>P6:</strong> Code complete, not behavior-validated, not sealed. Do not assume validated.<br />
          <strong>P7:</strong> Sealed as LOCAL_APP_RELEASE_CANDIDATE.<br />
          <strong>P8:</strong> Sealed as REAL_PROVIDER_READY_LOCAL_APP.<br />
          <strong>Provider output:</strong> Unverified and advisory only. You remain responsible for all scores.
        </p>
      </div>
    </div>
  )
}
