import type { ButtonHTMLAttributes, ReactNode } from 'react'

const accentColors: Record<string, string> = {
  green: '#0ae448',
  pink: '#f100cb',
  orange: '#ff8709',
  lilac: '#9d95ff',
  blue: '#00bae2',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  accent?: keyof typeof accentColors
  children: ReactNode
}

export function Button({ variant = 'primary', accent = 'green', children, className = '', ...props }: ButtonProps) {
  const color = accentColors[accent] || accentColors.green

  const base = 'inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed'

  const variants: Record<string, string> = {
    primary: `${base} px-5 py-2.5 text-sm rounded-[9999px] border-none`,
    secondary: `${base} px-5 py-2.5 text-sm rounded-[9999px] border border-border bg-transparent`,
    ghost: `${base} px-3 py-1.5 text-sm rounded-lg border-none bg-transparent`,
    danger: `${base} px-5 py-2.5 text-sm rounded-[9999px] border-none`,
  }

  const styles: Record<string, React.CSSProperties> = {
    primary: { backgroundColor: color, color: '#0e100f' },
    secondary: { color: '#fffce1' },
    ghost: { color: '#c4c2b8' },
    danger: { backgroundColor: '#ff4444', color: '#fff' },
  }

  return (
    <button
      className={`${variants[variant]} hover:opacity-90 active:scale-[0.97] ${className}`}
      style={styles[variant]}
      {...props}
    >
      {children}
    </button>
  )
}
