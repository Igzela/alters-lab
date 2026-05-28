import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'

interface FieldProps {
  label: string
  children: React.ReactNode
  className?: string
}

export function Field({ label, children, className = '' }: FieldProps) {
  return (
    <label className={`grid gap-1.5 mb-3 ${className}`}>
      <span className="text-xs font-medium" style={{ color: '#7c7c6f' }}>{label}</span>
      {children}
    </label>
  )
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className = '', ...props }: InputProps) {
  return (
    <input
      className={`w-full px-3 py-2 text-sm rounded-lg border border-border outline-none transition-colors focus:border-accent ${className}`}
      style={{ backgroundColor: '#1a1c1a', color: '#fffce1' }}
      {...props}
    />
  )
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

export function Select({ className = '', children, ...props }: SelectProps) {
  return (
    <select
      className={`w-full px-3 py-2 text-sm rounded-lg border border-border outline-none transition-colors focus:border-accent ${className}`}
      style={{ backgroundColor: '#1a1c1a', color: '#fffce1' }}
      {...props}
    >
      {children}
    </select>
  )
}

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

export function TextArea({ className = '', ...props }: TextAreaProps) {
  return (
    <textarea
      className={`w-full px-3 py-2 text-sm rounded-lg border border-border outline-none transition-colors focus:border-accent font-mono ${className}`}
      style={{ backgroundColor: '#1a1c1a', color: '#fffce1' }}
      {...props}
    />
  )
}
