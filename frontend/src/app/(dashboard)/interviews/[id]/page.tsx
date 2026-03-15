'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { interviewsApi, plansApi, aiApi } from '@/lib/api-client';
import type { Interview, Plan, Analysis, SubmitAnswerRequest, Question } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/input';
import { PageLoader, Spinner } from '@/components/ui/spinner';
import axios from 'axios';

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round((score / 10) * 100);
  const color = score >= 7 ? 'var(--color-success)' : score >= 4 ? 'var(--color-gold)' : 'var(--color-danger)';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="text-sm font-semibold" style={{ color }}>{score.toFixed(1)}</span>
    </div>
  );
}

function AnalysisCard({ analysis }: { analysis: Analysis }) {
  return (
    <div className="mt-3 p-3 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)]">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">AI Анализ</p>
        <Badge value={analysis.recommendation} />
      </div>
      <ScoreBar score={analysis.score} />
      <p className="text-sm text-[var(--color-text)] mt-2 leading-relaxed">{analysis.summary}</p>
      {analysis.strengths.length > 0 && (
        <div className="mt-2">
          <p className="text-xs text-[var(--color-success)] mb-1">Сильные стороны</p>
          <ul className="text-xs text-[var(--color-text-muted)] space-y-0.5">
            {analysis.strengths.map((s, i) => <li key={i}>• {s}</li>)}
          </ul>
        </div>
      )}
      {analysis.weaknesses.length > 0 && (
        <div className="mt-2">
          <p className="text-xs text-[var(--color-danger)] mb-1">Слабые стороны</p>
          <ul className="text-xs text-[var(--color-text-muted)] space-y-0.5">
            {analysis.weaknesses.map((w, i) => <li key={i}>• {w}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

function ExpectedAnswerBlock({ question }: { question: Question }) {
  const [show, setShow] = useState(false);
  const [expected, setExpected] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoad = async () => {
    if (expected) { setShow(true); return; }
    setLoading(true);
    setError('');
    try {
      const result = await aiApi.expectedAnswer({
        question: question.text,
        criteria: question.criteria,
        context: question.type,
      });
      setExpected(result.answer);
      setShow(true);
    } catch {
      setError('AI недоступен');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-2">
      {!show ? (
        <button
          type="button"
          onClick={handleLoad}
          className="flex items-center gap-1.5 text-xs text-[var(--color-text-subtle)] hover:text-[var(--color-text-muted)] transition-colors"
        >
          {loading ? <Spinner className="w-3 h-3" /> : (
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          )}
          {loading ? 'Загружаю...' : 'Ожидаемый ответ'}
          {error && <span className="text-[var(--color-danger)]">— {error}</span>}
        </button>
      ) : (
        <div className="rounded-xl bg-[var(--color-surface-2)]/60 border border-[var(--color-border)] px-3 py-2">
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs text-[var(--color-text-subtle)] font-medium">Ожидаемый ответ</p>
            <button onClick={() => setShow(false)} className="text-xs text-[var(--color-text-subtle)] hover:text-[var(--color-text)]">скрыть</button>
          </div>
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="text-xs text-[var(--color-text-muted)] leading-relaxed mb-1 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="text-xs text-[var(--color-text-muted)] space-y-0.5 pl-3 list-disc mb-1">{children}</ul>,
              li: ({ children }) => <li className="leading-relaxed">{children}</li>,
              strong: ({ children }) => <strong className="font-semibold text-[var(--color-text)]">{children}</strong>,
              code: ({ children }) => <code className="font-mono bg-[var(--color-surface-3,#2a2a2a)] px-1 rounded text-[var(--color-text)]">{children}</code>,
            }}
          >{expected}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

function AnswerAnalysisSection({
  answerId,
  interviewId,
  existingAnalysis,
}: {
  answerId: number;
  interviewId: number;
  existingAnalysis: Analysis | null;
}) {
  const qc = useQueryClient();
  const [localAnalysis, setLocalAnalysis] = useState<Analysis | null>(existingAnalysis);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // sync if new analysis comes from parent (analyzeAll)
  if (existingAnalysis && !localAnalysis) setLocalAnalysis(existingAnalysis);

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await interviewsApi.analyzeAnswer(interviewId, answerId);
      setLocalAnalysis(result);
      qc.invalidateQueries({ queryKey: ['interview', interviewId] });
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        // Already exists but not in local state yet — refetch
        qc.invalidateQueries({ queryKey: ['interview', interviewId] });
      } else {
        setError('Ошибка анализа');
      }
    } finally {
      setLoading(false);
    }
  };

  if (localAnalysis) {
    return <AnalysisCard analysis={localAnalysis} />;
  }

  return (
    <div className="mt-2 flex items-center gap-2">
      <Button variant="ghost" size="sm" onClick={handleAnalyze} disabled={loading}>
        {loading ? <Spinner className="w-3.5 h-3.5" /> : (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        )}
        Анализ AI
      </Button>
      {error && <p className="text-xs text-[var(--color-danger)]">{error}</p>}
    </div>
  );
}

export default function InterviewDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const interviewId = parseInt(id);
  const router = useRouter();
  const qc = useQueryClient();

  const [activeQuestionId, setActiveQuestionId] = useState<number | null>(null);
  const [answerText, setAnswerText] = useState('');
  const [answerError, setAnswerError] = useState('');
  const [analyzingAll, setAnalyzingAll] = useState(false);

  const { data: interview, isLoading } = useQuery<Interview>({
    queryKey: ['interview', interviewId],
    queryFn: () => interviewsApi.get(interviewId),
  });

  const { data: plan } = useQuery<Plan>({
    queryKey: ['plan', interview?.plan_id],
    queryFn: () => plansApi.get(interview!.plan_id),
    enabled: !!interview?.plan_id,
  });

  const { mutate: beginInterview, isPending: beginning } = useMutation({
    mutationFn: () => interviewsApi.begin(interviewId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['interview', interviewId] }),
  });

  const { mutate: completeInterview, isPending: completing } = useMutation({
    mutationFn: () => interviewsApi.complete(interviewId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['interview', interviewId] }),
  });

  const { mutate: submitAnswer, isPending: submitting } = useMutation({
    mutationFn: (data: SubmitAnswerRequest) => interviewsApi.submitAnswer(interviewId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['interview', interviewId] });
      setActiveQuestionId(null);
      setAnswerText('');
    },
    onError: (err) => {
      if (axios.isAxiosError(err)) setAnswerError(err.response?.data?.detail ?? 'Ошибка');
    },
  });

  const handleAnalyzeAll = async () => {
    setAnalyzingAll(true);
    try {
      await interviewsApi.analyzeAll(interviewId);
      qc.invalidateQueries({ queryKey: ['interview', interviewId] });
    } finally {
      setAnalyzingAll(false);
    }
  };

  if (isLoading) return <PageLoader />;
  if (!interview) return <p className="text-[var(--color-text-muted)]">Интервью не найдено</p>;

  const questions = plan?.questions ?? [];
  const isInProgress = interview.status === 'in_progress';
  const isPending = interview.status === 'pending';
  const isCompleted = interview.status === 'completed';
  const answeredQuestionIds = new Set(interview.answers.map((a) => a.question_id));
  const hasUnanalyzed = interview.answers.some((a) => !a.analysis);

  return (
    <div>
      <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] mb-6 transition-colors">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Назад
      </button>

      {/* Header */}
      <div className="flex items-start justify-between mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-2xl font-bold text-[var(--color-text)]">{interview.candidate_name}</h1>
            <Badge value={interview.status} />
          </div>
          <p className="text-sm text-[var(--color-text-muted)]">
            {interview.type} · План #{interview.plan_id} · {interview.answers.length} из {questions.length} ответов
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {isPending && (
            <Button onClick={() => beginInterview()} loading={beginning}>
              Начать интервью
            </Button>
          )}
          {isInProgress && (
            <>
              {hasUnanalyzed && interview.answers.length > 0 && (
                <Button variant="secondary" size="sm" onClick={handleAnalyzeAll} disabled={analyzingAll}>
                  {analyzingAll && <Spinner className="w-4 h-4" />}
                  Анализировать всё
                </Button>
              )}
              <Button onClick={() => completeInterview()} loading={completing} variant="secondary">
                Завершить
              </Button>
            </>
          )}
          {isCompleted && hasUnanalyzed && (
            <Button variant="secondary" size="sm" onClick={handleAnalyzeAll} disabled={analyzingAll}>
              {analyzingAll && <Spinner className="w-4 h-4" />}
              Запустить анализ
            </Button>
          )}
        </div>
      </div>

      {/* Pending state */}
      {isPending && (
        <Card className="flex flex-col items-center py-12 text-center mb-6">
          <p className="text-[var(--color-text-muted)] mb-2">Интервью ожидает начала</p>
          <p className="text-sm text-[var(--color-text-subtle)]">Нажмите «Начать интервью» чтобы приступить к вопросам</p>
        </Card>
      )}

      {/* Questions */}
      {(isInProgress || isCompleted) && questions.length > 0 && (
        <div className="flex flex-col gap-4">
          {questions.map((q, idx) => {
            const answer = interview.answers.find((a) => a.question_id === q.id);
            const isAnswered = answeredQuestionIds.has(q.id);
            const isActive = activeQuestionId === q.id;

            return (
              <Card key={q.id} className={isActive ? 'border-[var(--color-gold)]/30' : ''}>
                {/* Question header */}
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs font-mono text-[var(--color-text-subtle)]">#{idx + 1}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--color-surface-2)] text-[var(--color-text-muted)]">{q.type}</span>
                      {isAnswered && <span className="text-xs text-[var(--color-success)]">✓ Отвечено</span>}
                    </div>
                    <p className="text-sm text-[var(--color-text)] leading-relaxed">{q.text}</p>
                    {q.criteria.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {q.criteria.map((c, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-gold)]/10 text-[var(--color-gold)]">
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {isInProgress && !isAnswered && !isActive && (
                    <Button size="sm" variant="secondary" onClick={() => setActiveQuestionId(q.id)}>
                      Записать ответ
                    </Button>
                  )}
                </div>

                {/* Expected answer (for in_progress — HR helper) */}
                {isInProgress && !isActive && (
                  <ExpectedAnswerBlock question={q} />
                )}

                {/* Answer form */}
                {isActive && (
                  <div className="border-t border-[var(--color-border)] pt-4 mt-3">
                    <Textarea
                      label="Ответ кандидата"
                      placeholder="Запишите ответ..."
                      rows={4}
                      value={answerText}
                      onChange={(e) => setAnswerText(e.target.value)}
                      autoFocus
                    />
                    {answerError && <p className="text-sm text-[var(--color-danger)] mt-1">{answerError}</p>}
                    <div className="flex gap-2 justify-end mt-3">
                      <Button variant="ghost" size="sm" onClick={() => { setActiveQuestionId(null); setAnswerText(''); }}>
                        Отмена
                      </Button>
                      <Button size="sm" loading={submitting}
                        onClick={() => {
                          if (!answerText.trim()) { setAnswerError('Введите ответ'); return; }
                          setAnswerError('');
                          submitAnswer({ question_id: q.id, answer: answerText });
                        }}>
                        Сохранить ответ
                      </Button>
                    </div>
                  </div>
                )}

                {/* Saved answer + analysis */}
                {answer && !isActive && (
                  <div className="border-t border-[var(--color-border)] pt-3 mt-3">
                    <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">Ответ кандидата</p>
                    <p className="text-sm text-[var(--color-text)] leading-relaxed bg-[var(--color-surface-2)] px-3 py-2.5 rounded-xl">
                      {answer.answer}
                    </p>
                    <AnswerAnalysisSection
                      answerId={answer.id}
                      interviewId={interviewId}
                      existingAnalysis={answer.analysis}
                    />
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
