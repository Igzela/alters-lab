import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'

interface FieldProps {
  label: string
  children: React.ReactNode
  className?: string
}

export function Field({ label, children, className = '' }: FieldProps) {
  return (
    <label className={`grid gap-1.5 mb-3 ${className}`}>
      <span className="text-xs font-medium" style={{ color: '#78716c' }}>{label}</span>
      {children}
    </label>
  )
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className = '', ...props }: InputProps) {
  return (
    <input
      className={`w-full px-3 py-2 text-sm rounded-lg border outline-none transition-colors focus:border-[#b45309] focus:ring-1 focus:ring-[#b45309]/20 ${className}`}
      style={{ backgroundColor: '#ffffff', color: '#1c1917', borderColor: '#e8e6e1' }}
      {...props}
    />
  )
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

export function Select({ className = '', children, ...props }: SelectProps) {
  return (
    <select
      className={`w-full px-3 py-2 text-sm rounded-lg border outline-none transition-colors focus:border-[#b45309] focus:ring-1 focus:ring-[#b45309]/20 ${className}`}
      style={{ backgroundColor: '#ffffff', color: '#1c1917', borderColor: '#e8e6e1' }}
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
      className={`w-full px-3 py-2 text-sm rounded-lg border outline-none transition-colors focus:border-[#b45309] focus:ring-1 focus:ring-[#b45309]/20 font-mono ${className}`}
      style={{ backgroundColor: '#ffffff', color: '#1c1917', borderColor: '#e8e6e1' }}
      {...props}
    />
  )
}
