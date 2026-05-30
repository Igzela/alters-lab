import { createContext, useContext, useState, useCallback, useRef } from 'react'
import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'

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

const VARIANT_STYLES: Record<ToastVariant, { bg: string; border: string; color: string; icon: string }> = {
  success: { bg: 'var(--color-success-light)', border: 'color-mix(in srgb, var(--color-success) 25%, var(--color-success-light))', color: 'var(--color-success)', icon: '✓' },
  error: { bg: 'var(--color-error-light)', border: 'color-mix(in srgb, var(--color-error) 25%, var(--color-error-light))', color: 'var(--color-error)', icon: '✕' },
  warning: { bg: 'var(--color-warning-light)', border: 'color-mix(in srgb, var(--color-warning) 25%, var(--color-warning-light))', color: 'var(--color-warning)', icon: '!' },
  info: { bg: 'var(--color-info-light)', border: 'color-mix(in srgb, var(--color-info) 25%, var(--color-info-light))', color: 'var(--color-info)', icon: 'i' },
}

function ToastItemView({ toast, onDismiss }: { toast: ToastItem; onDismiss: (id: string) => void }) {
  const { t } = useTranslation()
  const style = VARIANT_STYLES[toast.variant]

  return (
    <div
      role={toast.variant === 'error' ? 'alert' : undefined}
      aria-live={toast.variant === 'error' ? undefined : 'polite'}
      className="flex items-start gap-3 p-3 rounded-xl transition-all duration-300"
      style={{
        backgroundColor: style.bg,
        border: `1px solid ${style.border}`,
        boxShadow: '0 4px 12px rgba(28,25,23,0.1)',
      }}
    >
      <span className="text-sm font-bold flex-shrink-0 mt-0.5" style={{ color: style.color }}>{style.icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>{toast.title}</p>
        {toast.description && <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>{toast.description}</p>}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-xs flex-shrink-0 cursor-pointer border-none bg-transparent transition-colors"
        style={{ color: 'var(--color-text-muted)' }}
        aria-label={t('common.dismiss')}
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
