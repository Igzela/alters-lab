interface ErrorDisplayProps {
  message: string
  onRetry?: () => void
}

export default function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  return (
    <div className="p-3 bg-red-950/30 border border-red-800/50 rounded-lg text-sm text-red-400 flex items-start gap-2">
      <span className="flex-1">{message}</span>
      {onRetry && (
        <button
          className="text-xs text-red-300 hover:text-red-200 underline shrink-0"
          onClick={onRetry}
        >
          Retry
        </button>
      )}
    </div>
  )
}
