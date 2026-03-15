'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { interviewsApi, plansApi } from '@/lib/api-client';
import type { Interview, Plan, StartInterviewRequest } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { PageLoader } from '@/components/ui/spinner';
import axios from 'axios';

const INTERVIEW_TYPES = ['technical', 'behavioral', 'mixed', 'hr'];

function StartInterviewModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<StartInterviewRequest>({ plan_id: 0, candidate_name: '', type: 'technical' });
  const [error, setError] = useState('');

  const { data: plans } = useQuery<Plan[]>({
    queryKey: ['plans', 'for-interview-modal'],
    queryFn: () => plansApi.list({ page: 1, page_size: 100 }),
    staleTime: 0,
  });

  const publishedPlans = plans?.filter((p) => p.status === 'published') ?? [];

  const { mutate, isPending } = useMutation({
    mutationFn: (data: StartInterviewRequest) => interviewsApi.start(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['interviews'] });
      onClose();
    },
    onError: (err) => {
      if (axios.isAxiosError(err)) setError(err.response?.data?.detail ?? 'Ошибка');
      else setError('Ошибка создания интервью');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.candidate_name.trim()) { setError('Введите имя кандидата'); return; }
    if (!form.plan_id) { setError('Выберите план'); return; }
    mutate(form);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-[var(--color-text)] mb-5">Новое интервью</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Имя кандидата"
            placeholder="Иванов Иван"
            value={form.candidate_name}
            onChange={(e) => setForm((f) => ({ ...f, candidate_name: e.target.value }))}
            autoFocus
          />
          <div>
            <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1.5">План интервью</p>
            {publishedPlans.length === 0 ? (
              <p className="text-sm text-[var(--color-danger)]">
                Нет опубликованных планов.{' '}
                <Link href="/plans" className="underline text-[var(--color-gold)]">Создайте и опубликуйте план.</Link>
              </p>
            ) : (
              <select
                value={form.plan_id}
                onChange={(e) => setForm((f) => ({ ...f, plan_id: parseInt(e.target.value) }))}
                className="w-full h-10 px-3 rounded-xl text-sm bg-[var(--color-surface-2)] text-[var(--color-text)] border border-[var(--color-border)] outline-none focus:border-[var(--color-gold)]"
              >
                <option value={0} disabled>Выберите план</option>
                {publishedPlans.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} ({p.questions.length} вопр.)</option>
                ))}
              </select>
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1.5">Тип</p>
            <select
              value={form.type}
              onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
              className="w-full h-10 px-3 rounded-xl text-sm bg-[var(--color-surface-2)] text-[var(--color-text)] border border-[var(--color-border)] outline-none focus:border-[var(--color-gold)]"
            >
              {INTERVIEW_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
          <div className="flex gap-2 justify-end mt-2">
            <Button type="button" variant="ghost" onClick={onClose}>Отмена</Button>
            <Button type="submit" loading={isPending} disabled={publishedPlans.length === 0}>Создать</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function InterviewsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const qc = useQueryClient();

  const { data: interviews, isLoading } = useQuery<Interview[]>({
    queryKey: ['interviews'],
    queryFn: () => interviewsApi.list({ page: 1, page_size: 50 }),
  });

  const { mutate: deleteInterview } = useMutation({
    mutationFn: (id: number) => interviewsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['interviews'] }),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]">Интервью</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            {interviews?.length ?? 0} интервью
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Начать интервью
        </Button>
      </div>

      {isLoading ? (
        <PageLoader />
      ) : interviews?.length === 0 ? (
        <Card className="flex flex-col items-center py-16 text-center">
          <div className="w-14 h-14 rounded-2xl bg-[var(--color-surface-2)] flex items-center justify-center mb-4">
            <svg className="w-7 h-7 text-[var(--color-text-subtle)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
            </svg>
          </div>
          <p className="text-[var(--color-text-muted)] font-medium mb-1">Интервью пока нет</p>
          <p className="text-sm text-[var(--color-text-subtle)] mb-5">Создайте план и начните первое интервью</p>
          <Button onClick={() => setShowCreate(true)}>Начать интервью</Button>
        </Card>
      ) : (
        <div className="grid gap-3">
          {interviews?.map((interview) => (
            <Link key={interview.id} href={`/interviews/${interview.id}`}>
              <Card hoverable className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 mb-1">
                    <span className="text-sm font-semibold text-[var(--color-text)] truncate">
                      {interview.candidate_name}
                    </span>
                    <Badge value={interview.status} />
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {interview.type} · План #{interview.plan_id} · {interview.answers.length} ответов
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      if (confirm('Удалить интервью?')) deleteInterview(interview.id);
                    }}
                    className="p-2 rounded-lg text-[var(--color-text-subtle)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 transition-all"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                  <svg className="w-4 h-4 text-[var(--color-text-subtle)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {showCreate && <StartInterviewModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
