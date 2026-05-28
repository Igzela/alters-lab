import { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react'
import type { ReactNode } from 'react'

type ToastVariant = 'success' | 'error' | 'warning' | 'info'

interface ToastItem {
  id: string
  title: string
  description?: string
  variant: ToastVariant
}

interface ToastInput {
  title: string
  description?: string
  variant?: ToastVariant
  durationMs?: number
}

interface ToastContextValue {
  toast: (input: ToastInput) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

const VARIANT_STYLES: Record<ToastVariant, { bg: string; border: string; icon: string }> = {
  success: { bg: 'rgba(10, 228, 72, 0.1)', border: 'rgba(10, 228, 72, 0.3)', icon: '✓' },
  error: { bg: 'rgba(255, 68, 68, 0.1)', border: 'rgba(255, 68, 68, 0.3)', icon: '✕' },
  warning: { bg: 'rgba(255, 135, 9, 0.1)', border: 'rgba(255, 135, 9, 0.3)', icon: '!' },
  info: { bg: 'rgba(0, 186, 226, 0.1)', border: 'rgba(0, 186, 226, 0.3)', icon: 'i' },
}

function ToastItemView({ toast, onDismiss }: { toast: ToastItem; onDismiss: (id: string) => void }) {
  const style = VARIANT_STYLES[toast.variant]

  return (
    <div
      role={toast.variant === 'error' ? 'alert' : undefined}
      aria-live={toast.variant === 'error' ? undefined : 'polite'}
      className="flex items-start gap-3 p-3 rounded-xl transition-all duration-300"
      style={{
        backgroundColor: style.bg,
        border: `1px solid ${style.border}`,
        backdropFilter: 'blur(8px)',
      }}
    >
      <span className="text-sm font-bold flex-shrink-0 mt-0.5" style={{ color: style.border }}>{style.icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium" style={{ color: '#fffce1' }}>{toast.title}</p>
        {toast.description && <p className="text-xs mt-0.5" style={{ color: '#7c7c6f' }}>{toast.description}</p>}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-xs flex-shrink-0 cursor-pointer border-none bg-transparent transition-colors"
        style={{ color: '#7c7c6f' }}
        aria-label="Dismiss"
      >
        ✕
      </button>
    </div>
  )
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const counterRef = useRef(0)

  const dismiss = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const toast = useCallback((input: ToastInput) => {
    const id = `toast-${++counterRef.current}`
    const item: ToastItem = {
      id,
      title: input.title,
      description: input.description,
      variant: input.variant || 'info',
    }
    setToasts(prev => {
      const next = [...prev, item]
      return next.length > 3 ? next.slice(-3) : next
    })
    setTimeout(() => dismiss(id), input.durationMs || 5000)
  }, [dismiss])

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div
        className="fixed top-4 right-4 z-50 flex flex-col gap-2"
        style={{ maxWidth: '360px', width: '100%', pointerEvents: 'none' }}
      >
        {toasts.map(t => (
          <div key={t.id} className="toast-enter" style={{ pointerEvents: 'auto' }}>
            <ToastItemView toast={t} onDismiss={dismiss} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
