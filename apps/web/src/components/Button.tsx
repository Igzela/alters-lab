import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  children: ReactNode
}

export function Button({ variant = 'primary', children, className = '', style: styleProp, ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'

  const variants: Record<string, string> = {
    primary: `${base} px-5 py-2.5 text-sm rounded-full border-none`,
    secondary: `${base} px-5 py-2.5 text-sm rounded-full border`,
    ghost: `${base} px-3 py-1.5 text-sm rounded-lg border-none bg-transparent hover:bg-[var(--color-surface-raised)]`,
    danger: `${base} px-5 py-2.5 text-sm rounded-full border-none`,
  }

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: { backgroundColor: 'var(--color-accent)', color: '#ffffff', '--tw-ring-color': 'var(--color-accent)' } as React.CSSProperties,
    secondary: { color: 'var(--color-text)', borderColor: 'var(--color-border)', '--tw-ring-color': 'var(--color-border)' } as React.CSSProperties,
    ghost: { color: 'var(--color-text-secondary)', '--tw-ring-color': 'var(--color-border)' } as React.CSSProperties,
    danger: { backgroundColor: 'var(--color-error)', color: '#ffffff', '--tw-ring-color': 'var(--color-error)' } as React.CSSProperties,
  }

  return (
    <button
      className={`${variants[variant]} hover:opacity-90 active:scale-[0.97] focus-visible:ring-[var(--tw-ring-color)] ${className}`}
      style={{ ...variantStyles[variant], ...styleProp }}
      {...props}
    >
      {children}
    </button>
  )
}
