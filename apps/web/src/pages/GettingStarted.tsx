type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started'

export default function GettingStarted({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const section = 'mb-6 p-4 border border-gray-700 rounded-lg'

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Getting Started</h2>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">1. Provider is disabled by default</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          Alters Lab starts with provider mode <strong>disabled</strong>. No LLM calls, no API key needed.
          Switch to <strong>mock</strong> mode in Provider Settings to test dialogue features without network calls.
        </p>
        <button className="mt-2 px-3 py-1.5 text-xs bg-gray-800 text-white rounded hover:bg-gray-700" onClick={() => onNavigate('provider')}>
          Open Provider Settings
        </button>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">2. Run your first Weekly Review</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          Paste a weekly note, review extracted records, score your action alignment.
          Each review creates calibration data that tracks your patterns over time.
        </p>
        <button className="mt-2 px-3 py-1.5 text-xs bg-gray-800 text-white rounded hover:bg-gray-700" onClick={() => onNavigate('weekly')}>
          Start Weekly Review
        </button>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">3. Check system health</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          Run <code className="bg-gray-800 px-1 rounded">alters-lab doctor</code> in your terminal to verify installation, config, data directories, and provider mode.
        </p>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">4. Back up before risky changes</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          Run <code className="bg-gray-800 px-1 rounded">alters-lab backup</code> to create a snapshot of your data.
          User data persists across restarts and is not removed on uninstall.
        </p>
      </div>

      <div className="mb-6 p-4 border border-gray-600 rounded-lg">
        <h3 className="text-sm font-medium mb-2">Boundaries</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          <strong>P6:</strong> Code complete, not behavior-validated, not sealed. Do not assume validated.<br />
          <strong>P7:</strong> Sealed as LOCAL_APP_RELEASE_CANDIDATE.<br />
          <strong>P8:</strong> Sealed as REAL_PROVIDER_READY_LOCAL_APP.<br />
          <strong>Provider output:</strong> Unverified and advisory only. You remain responsible for all scores.
        </p>
      </div>
    </div>
  )
}
