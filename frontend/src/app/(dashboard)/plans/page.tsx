'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { plansApi, aiApi } from '@/lib/api-client';
import type { Plan, CreatePlanRequest, AiGeneratedPlan } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import { PageLoader, Spinner } from '@/components/ui/spinner';
import axios from 'axios';

type ModalTab = 'manual' | 'ai';

function CreatePlanModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [tab, setTab] = useState<ModalTab>('manual');

  // Manual form
  const [form, setForm] = useState<CreatePlanRequest>({ name: '', description: '' });
  const [formError, setFormError] = useState('');

  // AI form
  const [aiPrompt, setAiPrompt] = useState('');
  const [questionCount, setQuestionCount] = useState(8);
  const [aiPreview, setAiPreview] = useState<AiGeneratedPlan | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  const { mutate: createPlan, isPending: creating } = useMutation({
    mutationFn: (data: CreatePlanRequest) => plansApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plans'] });
      onClose();
    },
    onError: (err) => {
      if (axios.isAxiosError(err)) setFormError(err.response?.data?.detail ?? 'Ошибка создания');
      else setFormError('Ошибка создания плана');
    },
  });

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) { setFormError('Введите название'); return; }
    createPlan(form);
  };

  const handleAiGenerate = async () => {
    if (!aiPrompt.trim()) { setAiError('Опишите план'); return; }
    setAiError('');
    setAiLoading(true);
    try {
      const result = await aiApi.generatePlan({ prompt: aiPrompt, question_count: questionCount });
      setAiPreview(result);
    } catch (err) {
      if (axios.isAxiosError(err)) setAiError(err.response?.data?.detail ?? 'Ошибка AI');
      else setAiError('AI недоступен');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAiSave = () => {
    if (!aiPreview) return;
    createPlan({
      name: aiPreview.name,
      description: aiPreview.description,
      questions: aiPreview.questions,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-semibold text-[var(--color-text)] mb-5">Новый план</h2>

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-[var(--color-surface-2)] rounded-xl mb-5">
          {(['manual', 'ai'] as ModalTab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 h-8 rounded-lg text-sm font-medium transition-all ${
                tab === t
                  ? 'bg-[var(--color-gold)] text-[#0D0D0D]'
                  : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)]'
              }`}
            >
              {t === 'manual' ? 'Вручную' : '✨ Через AI'}
            </button>
          ))}
        </div>

        {tab === 'manual' ? (
          <form onSubmit={handleManualSubmit} className="flex flex-col gap-4">
            <Input
              label="Название"
              placeholder="Например: Senior Frontend Developer"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              autoFocus
            />
            <Textarea
              label="Описание (необязательно)"
              placeholder="Для чего этот план?"
              rows={3}
              value={form.description ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
            {formError && <p className="text-sm text-[var(--color-danger)]">{formError}</p>}
            <div className="flex gap-2 justify-end mt-2">
              <Button type="button" variant="ghost" onClick={onClose}>Отмена</Button>
              <Button type="submit" loading={creating}>Создать</Button>
            </div>
          </form>
        ) : (
          <div className="flex flex-col gap-4">
            {!aiPreview ? (
              <>
                <Textarea
                  label="Опишите план"
                  placeholder="Например: Senior Python разработчик, FastAPI, PostgreSQL, микросервисы, 3+ года опыта"
                  rows={4}
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  autoFocus
                />
                <div className="flex items-center gap-3">
                  <label className="text-sm font-medium text-[var(--color-text-muted)] whitespace-nowrap">
                    Вопросов:
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    value={questionCount}
                    onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                    className="w-20 h-10 px-3 rounded-xl text-sm bg-[var(--color-surface-2)] text-[var(--color-text)] border border-[var(--color-border)] outline-none focus:border-[var(--color-gold)]"
                  />
                </div>
                {aiError && <p className="text-sm text-[var(--color-danger)]">{aiError}</p>}
                <div className="flex gap-2 justify-end mt-2">
                  <Button type="button" variant="ghost" onClick={onClose}>Отмена</Button>
                  <Button onClick={handleAiGenerate} loading={aiLoading}>
                    Сгенерировать
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="p-3 rounded-xl bg-[var(--color-gold)]/5 border border-[var(--color-gold)]/20">
                  <p className="text-sm font-semibold text-[var(--color-text)] mb-0.5">{aiPreview.name}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">{aiPreview.description}</p>
                </div>
                <div className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1">
                  {aiPreview.questions.map((q, i) => (
                    <div key={i} className="p-3 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)]">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono text-[var(--color-text-subtle)]">#{i + 1}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--color-border)] text-[var(--color-text-muted)]">{q.type}</span>
                      </div>
                      <p className="text-sm text-[var(--color-text)]">{q.text}</p>
                      {q.criteria.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1.5">
                          {q.criteria.map((c, ci) => (
                            <span key={ci} className="text-xs px-1.5 py-0.5 rounded-full bg-[var(--color-gold)]/10 text-[var(--color-gold)]">{c}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 justify-end mt-2">
                  <Button variant="ghost" onClick={() => setAiPreview(null)}>← Назад</Button>
                  <Button onClick={handleAiSave} loading={creating}>Сохранить план</Button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function PlansPage() {
  const [showCreate, setShowCreate] = useState(false);
  const qc = useQueryClient();

  const { data: plans, isLoading } = useQuery<Plan[]>({
    queryKey: ['plans'],
    queryFn: () => plansApi.list({ page: 1, page_size: 50 }),
  });

  const { mutate: deletePlan } = useMutation({
    mutationFn: (id: number) => plansApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plans'] }),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]">Планы интервью</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            {plans?.length ?? 0} {plans?.length === 1 ? 'план' : 'планов'}
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Создать план
        </Button>
      </div>

      {isLoading ? (
        <PageLoader />
      ) : plans?.length === 0 ? (
        <Card className="flex flex-col items-center py-16 text-center">
          <div className="w-14 h-14 rounded-2xl bg-[var(--color-surface-2)] flex items-center justify-center mb-4">
            <svg className="w-7 h-7 text-[var(--color-text-subtle)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p className="text-[var(--color-text-muted)] font-medium mb-1">Планов пока нет</p>
          <p className="text-sm text-[var(--color-text-subtle)] mb-5">Создайте первый план интервью</p>
          <Button onClick={() => setShowCreate(true)}>Создать план</Button>
        </Card>
      ) : (
        <div className="grid gap-3">
          {plans?.map((plan) => (
            <Link key={plan.id} href={`/plans/${plan.id}`}>
              <Card hoverable className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 mb-1">
                    <span className="text-sm font-semibold text-[var(--color-text)] truncate">{plan.name}</span>
                    <Badge value={plan.status} />
                  </div>
                  {plan.description && (
                    <p className="text-xs text-[var(--color-text-muted)] truncate">{plan.description}</p>
                  )}
                  <p className="text-xs text-[var(--color-text-subtle)] mt-1">{plan.questions.length} вопросов</p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      if (confirm('Удалить план?')) deletePlan(plan.id);
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

      {showCreate && <CreatePlanModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
