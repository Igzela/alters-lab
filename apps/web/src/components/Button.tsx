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
    ghost: `${base} px-3 py-1.5 text-sm rounded-lg border-none bg-transparent hover:bg-black/5`,
    danger: `${base} px-5 py-2.5 text-sm rounded-full border-none`,
  }

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: { backgroundColor: '#b45309', color: '#ffffff', '--tw-ring-color': '#b45309' } as React.CSSProperties,
    secondary: { color: '#1c1917', borderColor: '#e8e6e1', '--tw-ring-color': '#d6d3d1' } as React.CSSProperties,
    ghost: { color: '#78716c', '--tw-ring-color': '#d6d3d1' } as React.CSSProperties,
    danger: { backgroundColor: '#dc2626', color: '#ffffff', '--tw-ring-color': '#dc2626' } as React.CSSProperties,
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
