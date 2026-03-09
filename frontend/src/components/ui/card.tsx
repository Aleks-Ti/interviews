interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function Card({ children, className = '', onClick, hoverable }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={`
        bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-5
        ${hoverable ? 'cursor-pointer hover:border-[var(--color-border-hover)] hover:bg-[var(--color-surface-2)] transition-all duration-150' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`mb-4 ${className}`}>{children}</div>;
}

export function CardTitle({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <h3 className={`text-base font-semibold text-[var(--color-text)] ${className}`}>{children}</h3>;
}
