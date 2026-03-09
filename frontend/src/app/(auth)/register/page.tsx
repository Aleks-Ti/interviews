'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { authApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import axios from 'axios';

export default function RegisterPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);

  const [form, setForm] = useState({ email: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.email) errs.email = 'Введите email';
    if (form.password.length < 8) errs.password = 'Минимум 8 символов';
    if (form.password !== form.confirmPassword) errs.confirmPassword = 'Пароли не совпадают';
    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }
    setErrors({});
    setLoading(true);
    try {
      await api.post('/user', { email: form.email, password: form.password, role_id: 2 });
      await authApi.login({ email: form.email, password: form.password });
      const { data: user } = await authApi.me();
      setUser(user);
      router.push('/dashboard');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setErrors({ general: err.response?.data?.detail ?? 'Ошибка регистрации' });
      } else {
        setErrors({ general: 'Ошибка регистрации' });
      }
    } finally {
      setLoading(false);
    }
  };

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)] px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-10">
          <div className="w-12 h-12 rounded-2xl bg-[var(--color-gold)] flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-[#0D0D0D]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[var(--color-text)] tracking-tight">Interview Room</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">Создайте аккаунт</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Email"
              type="email"
              placeholder="you@company.com"
              value={form.email}
              onChange={set('email')}
              error={errors.email}
              required
              autoFocus
            />
            <Input
              label="Пароль"
              type="password"
              placeholder="Мин. 8 символов, A-z, 0-9, спецсимвол"
              value={form.password}
              onChange={set('password')}
              error={errors.password}
              required
            />
            <Input
              label="Подтвердите пароль"
              type="password"
              placeholder="••••••••"
              value={form.confirmPassword}
              onChange={set('confirmPassword')}
              error={errors.confirmPassword}
              required
            />

            {errors.general && (
              <p className="text-sm text-[var(--color-danger)] text-center">{errors.general}</p>
            )}

            <Button type="submit" loading={loading} size="lg" className="mt-2 w-full">
              Зарегистрироваться
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-[var(--color-text-muted)] mt-6">
          Уже есть аккаунт?{' '}
          <Link href="/login" className="text-[var(--color-gold)] hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
}
