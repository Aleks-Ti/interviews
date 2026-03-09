'use client';

import { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-[var(--color-text-muted)]"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`
            h-10 px-3 rounded-xl text-sm
            bg-[var(--color-surface-2)] text-[var(--color-text)]
            border ${error ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]'}
            placeholder:text-[var(--color-text-subtle)]
            outline-none
            focus:border-[var(--color-gold)] focus:ring-2 focus:ring-[var(--color-gold)]/20
            transition-all duration-150
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="text-xs text-[var(--color-danger)]">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-[var(--color-text-muted)]"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={`
            px-3 py-2.5 rounded-xl text-sm resize-none
            bg-[var(--color-surface-2)] text-[var(--color-text)]
            border ${error ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]'}
            placeholder:text-[var(--color-text-subtle)]
            outline-none
            focus:border-[var(--color-gold)] focus:ring-2 focus:ring-[var(--color-gold)]/20
            transition-all duration-150
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="text-xs text-[var(--color-danger)]">{error}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
