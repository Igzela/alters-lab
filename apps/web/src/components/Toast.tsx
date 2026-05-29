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
  success: { bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a', icon: '✓' },
  error: { bg: '#fef2f2', border: '#fecaca', color: '#dc2626', icon: '✕' },
  warning: { bg: '#fffbeb', border: '#fde68a', color: '#d97706', icon: '!' },
  info: { bg: '#eff6ff', border: '#bfdbfe', color: '#2563eb', icon: 'i' },
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
        <p className="text-sm font-medium" style={{ color: '#1c1917' }}>{toast.title}</p>
        {toast.description && <p className="text-xs mt-0.5" style={{ color: '#78716c' }}>{toast.description}</p>}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="text-xs flex-shrink-0 cursor-pointer border-none bg-transparent transition-colors"
        style={{ color: '#a8a29e' }}
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
