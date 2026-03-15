'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { plansApi, questionsApi, aiApi } from '@/lib/api-client';
import type { Plan, CreateQuestionRequest, UpdatePlanRequest } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import { PageLoader, Spinner } from '@/components/ui/spinner';
import axios from 'axios';

function AddQuestionForm({ planId, planName, onDone }: { planId: number; planName: string; onDone: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<CreateQuestionRequest>({ text: '', type: 'open', criteria: [''] });
  const [error, setError] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiContext, setAiContext] = useState('');
  const [showAiHelper, setShowAiHelper] = useState(false);

  const { mutate, isPending } = useMutation({
    mutationFn: (data: CreateQuestionRequest) => questionsApi.create(planId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plan', planId] });
      onDone();
    },
    onError: (err) => {
      if (axios.isAxiosError(err)) setError(err.response?.data?.detail ?? 'Ошибка');
    },
  });

  const handleAiSuggest = async () => {
    setAiLoading(true);
    setError('');
    try {
      const context = aiContext || planName;
      const result = await aiApi.suggestQuestion({ context, question_type: form.type });
      setForm((f) => ({ ...f, text: result.text, type: result.type, criteria: result.criteria.length ? result.criteria : f.criteria }));
      setShowAiHelper(false);
    } catch {
      setError('AI недоступен или не настроен');
    } finally {
      setAiLoading(false);
    }
  };

  const addCriteria = () => setForm((f) => ({ ...f, criteria: [...f.criteria, ''] }));
  const setCriteria = (i: number, val: string) =>
    setForm((f) => ({ ...f, criteria: f.criteria.map((c, idx) => (idx === i ? val : c)) }));
  const removeCriteria = (i: number) =>
    setForm((f) => ({ ...f, criteria: f.criteria.filter((_, idx) => idx !== i) }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const filtered = form.criteria.filter((c) => c.trim());
    if (!form.text.trim()) { setError('Введите текст вопроса'); return; }
    mutate({ ...form, criteria: filtered });
  };

  return (
    <Card className="border-[var(--color-gold)]/30 bg-[var(--color-gold)]/5">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* AI helper */}
        {showAiHelper ? (
          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium text-[var(--color-text-muted)]">Контекст для AI</p>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder={planName}
                value={aiContext}
                onChange={(e) => setAiContext(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAiSuggest())}
                className="flex-1 h-10 px-3 rounded-xl text-sm bg-[var(--color-surface)] text-[var(--color-text)] border border-[var(--color-gold)]/40 outline-none focus:border-[var(--color-gold)]"
                autoFocus
              />
              <Button type="button" size="sm" onClick={handleAiSuggest} loading={aiLoading}>
                Сгенерировать
              </Button>
              <Button type="button" size="sm" variant="ghost" onClick={() => setShowAiHelper(false)}>✕</Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-[var(--color-text-muted)]">Новый вопрос</p>
            <button
              type="button"
              onClick={() => setShowAiHelper(true)}
              className="flex items-center gap-1.5 text-xs text-[var(--color-gold)] hover:underline"
            >
              {aiLoading ? <Spinner className="w-3 h-3" /> : '✨'} Сгенерировать через AI
            </button>
          </div>
        )}
        <Textarea
          placeholder="Расскажите о вашем опыте с..."
          rows={2}
          value={form.text}
          onChange={(e) => setForm((f) => ({ ...f, text: e.target.value }))}
          autoFocus={!showAiHelper}
        />
        <div>
          <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1.5">Тип</p>
          <select
            value={form.type}
            onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
            className="h-10 px-3 rounded-xl text-sm bg-[var(--color-surface-2)] text-[var(--color-text)] border border-[var(--color-border)] outline-none focus:border-[var(--color-gold)]"
          >
            <option value="open">Открытый</option>
            <option value="technical">Технический</option>
            <option value="behavioral">Поведенческий</option>
            <option value="situational">Ситуационный</option>
          </select>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <p className="text-sm font-medium text-[var(--color-text-muted)]">Критерии оценки</p>
            <button type="button" onClick={addCriteria} className="text-xs text-[var(--color-gold)] hover:underline">+ Добавить</button>
          </div>
          <div className="flex flex-col gap-2">
            {form.criteria.map((c, i) => (
              <div key={i} className="flex gap-2">
                <Input
                  placeholder={`Критерий ${i + 1}`}
                  value={c}
                  onChange={(e) => setCriteria(i, e.target.value)}
                  className="flex-1"
                />
                {form.criteria.length > 1 && (
                  <button type="button" onClick={() => removeCriteria(i)}
                    className="px-2 text-[var(--color-text-subtle)] hover:text-[var(--color-danger)]">✕</button>
                )}
              </div>
            ))}
          </div>
        </div>
        {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
        <div className="flex gap-2 justify-end">
          <Button type="button" variant="ghost" onClick={onDone}>Отмена</Button>
          <Button type="submit" loading={isPending}>Добавить вопрос</Button>
        </div>
      </form>
    </Card>
  );
}

export default function PlanDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const planId = parseInt(id);
  const router = useRouter();
  const qc = useQueryClient();
  const [addingQuestion, setAddingQuestion] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameForm, setNameForm] = useState<UpdatePlanRequest>({});

  const { data: plan, isLoading } = useQuery<Plan>({
    queryKey: ['plan', planId],
    queryFn: () => plansApi.get(planId),
  });

  const { mutate: publishPlan, isPending: publishing } = useMutation({
    mutationFn: () => plansApi.publish(planId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plan', planId] });
      qc.invalidateQueries({ queryKey: ['plans'] });
    },
  });

  const { mutate: forkPlan, isPending: forking } = useMutation({
    mutationFn: () => plansApi.fork(planId),
    onSuccess: (forked) => router.push(`/plans/${forked.id}`),
  });

  const { mutate: deletePlan } = useMutation({
    mutationFn: () => plansApi.delete(planId),
    onSuccess: () => router.push('/plans'),
  });

  const { mutate: updatePlan, isPending: updating } = useMutation({
    mutationFn: (data: UpdatePlanRequest) => plansApi.update(planId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plan', planId] });
      setEditingName(false);
    },
  });

  const { mutate: deleteQuestion } = useMutation({
    mutationFn: (qid: number) => questionsApi.delete(planId, qid),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plan', planId] }),
  });

  const { mutate: reorderQuestions } = useMutation({
    mutationFn: (questions: { id: number; position: number }[]) =>
      questionsApi.reorder(planId, { questions }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plan', planId] }),
  });

  const handleMove = (idx: number, direction: 'up' | 'down') => {
    if (!plan) return;
    const qs = [...plan.questions];
    const swapIdx = direction === 'up' ? idx - 1 : idx + 1;
    [qs[idx], qs[swapIdx]] = [qs[swapIdx], qs[idx]];
    reorderQuestions(qs.map((q, i) => ({ id: q.id, position: i })));
  };

  if (isLoading) return <PageLoader />;
  if (!plan) return <p className="text-[var(--color-text-muted)]">План не найден</p>;

  const isDraft = plan.status === 'draft';

  return (
    <div>
      {/* Back */}
      <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] mb-6 transition-colors">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Назад
      </button>

      {/* Header */}
      <div className="flex items-start justify-between mb-8 gap-4">
        <div className="flex-1">
          {editingName ? (
            <div className="flex items-center gap-2">
              <Input
                value={nameForm.name ?? plan.name}
                onChange={(e) => setNameForm((f) => ({ ...f, name: e.target.value }))}
                autoFocus
                className="text-lg font-bold"
              />
              <Button size="sm" loading={updating} onClick={() => updatePlan(nameForm)}>Сохранить</Button>
              <Button size="sm" variant="ghost" onClick={() => setEditingName(false)}>Отмена</Button>
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl font-bold text-[var(--color-text)]">{plan.name}</h1>
              <Badge value={plan.status} />
              {isDraft && (
                <button onClick={() => { setEditingName(true); setNameForm({ name: plan.name, description: plan.description ?? '' }); }}
                  className="p-1 text-[var(--color-text-subtle)] hover:text-[var(--color-text)]">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
              )}
            </div>
          )}
          {plan.description && (
            <p className="text-sm text-[var(--color-text-muted)] mt-1">{plan.description}</p>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {isDraft ? (
            <>
              <Button variant="secondary" size="sm" onClick={() => publishPlan()} loading={publishing}>
                Опубликовать
              </Button>
              <Button variant="danger" size="sm" onClick={() => { if (confirm('Удалить план?')) deletePlan(); }}>
                Удалить
              </Button>
            </>
          ) : (
            <Button variant="secondary" size="sm" onClick={() => forkPlan()} loading={forking}>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Форк
            </Button>
          )}
        </div>
      </div>

      {/* Questions */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-[var(--color-text)]">
          Вопросы <span className="text-[var(--color-text-subtle)] font-normal">({plan.questions.length})</span>
        </h2>
        {isDraft && !addingQuestion && (
          <Button variant="secondary" size="sm" onClick={() => setAddingQuestion(true)}>
            + Добавить вопрос
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-3">
        {addingQuestion && (
          <AddQuestionForm planId={planId} planName={plan.name} onDone={() => setAddingQuestion(false)} />
        )}

        {plan.questions.length === 0 && !addingQuestion ? (
          <Card className="flex flex-col items-center py-12 text-center">
            <p className="text-[var(--color-text-muted)] mb-1">Вопросов пока нет</p>
            {isDraft && (
              <Button variant="ghost" size="sm" onClick={() => setAddingQuestion(true)} className="mt-2">
                + Добавить первый вопрос
              </Button>
            )}
          </Card>
        ) : (
          plan.questions.map((q, idx) => (
            <Card key={q.id} className="relative group">
              <div className="flex items-start gap-3">
                {/* Reorder controls */}
                {isDraft && (
                  <div className="flex flex-col gap-0.5 mt-0.5 shrink-0">
                    <button
                      onClick={() => handleMove(idx, 'up')}
                      disabled={idx === 0}
                      className="p-1 rounded text-[var(--color-text-subtle)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)] disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleMove(idx, 'down')}
                      disabled={idx === plan.questions.length - 1}
                      className="p-1 rounded text-[var(--color-text-subtle)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)] disabled:opacity-20 disabled:cursor-not-allowed transition-all"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                )}

                <div className="flex-1 flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs font-mono text-[var(--color-text-subtle)]">#{idx + 1}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--color-surface-2)] text-[var(--color-text-muted)]">{q.type}</span>
                    </div>
                    <p className="text-sm text-[var(--color-text)] leading-relaxed">{q.text}</p>
                    {q.criteria.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2.5">
                        {q.criteria.map((c, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-gold)]/10 text-[var(--color-gold)]">
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {isDraft && (
                    <button
                      onClick={() => { if (confirm('Удалить вопрос?')) deleteQuestion(q.id); }}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-[var(--color-text-subtle)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 transition-all"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
