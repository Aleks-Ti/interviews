type BadgeVariant = 'draft' | 'published' | 'pending' | 'in_progress' | 'completed' | 'hire' | 'consider' | 'reject' | 'default';

const styles: Record<BadgeVariant, string> = {
  draft:       'bg-[var(--color-text-subtle)]/20 text-[var(--color-text-muted)]',
  published:   'bg-[var(--color-gold)]/15 text-[var(--color-gold)]',
  pending:     'bg-[var(--color-info)]/15 text-[var(--color-info)]',
  in_progress: 'bg-[var(--color-warning)]/15 text-[var(--color-warning)]',
  completed:   'bg-[var(--color-success)]/15 text-[var(--color-success)]',
  hire:        'bg-[var(--color-success)]/15 text-[var(--color-success)]',
  consider:    'bg-[var(--color-warning)]/15 text-[var(--color-warning)]',
  reject:      'bg-[var(--color-danger)]/15 text-[var(--color-danger)]',
  default:     'bg-[var(--color-surface-2)] text-[var(--color-text-muted)]',
};

const labels: Record<string, string> = {
  draft: 'Черновик',
  published: 'Опубликован',
  pending: 'Ожидание',
  in_progress: 'В процессе',
  completed: 'Завершён',
  hire: 'Нанять',
  consider: 'На рассмотрение',
  reject: 'Отказать',
};

interface BadgeProps {
  value: string;
  className?: string;
}

export function Badge({ value, className = '' }: BadgeProps) {
  const variant = (value as BadgeVariant) in styles ? (value as BadgeVariant) : 'default';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${styles[variant]} ${className}`}>
      {labels[value] ?? value}
    </span>
  );
}
