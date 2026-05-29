import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-8" style={{ backgroundColor: '#faf9f7' }}>
          <div className="max-w-md w-full text-center space-y-4">
            <div className="text-4xl">⚠️</div>
            <h1 className="text-xl font-semibold" style={{ color: '#1c1917' }}>Something went wrong</h1>
            <p className="text-sm" style={{ color: '#78716c' }}>
              The app encountered an unexpected error. Try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer border-none transition-colors"
              style={{ backgroundColor: '#d97706', color: 'white' }}
            >
              Refresh page
            </button>
            {this.state.error && (
              <details className="text-left text-xs mt-4 p-3 rounded-lg" style={{ backgroundColor: '#f5f5f4', color: '#78716c' }}>
                <summary className="cursor-pointer mb-2">Error details</summary>
                <pre className="whitespace-pre-wrap break-words">{this.state.error.message}</pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
