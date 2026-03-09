'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { plansApi, interviewsApi } from '@/lib/api-client';
import { useAuthStore } from '@/store/auth';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageLoader } from '@/components/ui/spinner';
import type { Plan, Interview } from '@/lib/types';

function StatCard({ label, value, sub }: { label: string; value: number; sub?: string }) {
  return (
    <Card>
      <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">{label}</p>
      <p className="text-3xl font-bold text-[var(--color-text)]">{value}</p>
      {sub && <p className="text-xs text-[var(--color-text-subtle)] mt-0.5">{sub}</p>}
    </Card>
  );
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data: plans, isLoading: plansLoading } = useQuery<Plan[]>({
    queryKey: ['plans'],
    queryFn: () => plansApi.list({ page: 1, page_size: 100 }),
  });

  const { data: interviews, isLoading: interviewsLoading } = useQuery<Interview[]>({
    queryKey: ['interviews'],
    queryFn: () => interviewsApi.list({ page: 1, page_size: 100 }),
  });

  const isLoading = plansLoading || interviewsLoading;

  const stats = {
    totalPlans: plans?.length ?? 0,
    publishedPlans: plans?.filter((p) => p.status === 'published').length ?? 0,
    totalInterviews: interviews?.length ?? 0,
    completedInterviews: interviews?.filter((i) => i.status === 'completed').length ?? 0,
  };

  const recentInterviews = interviews?.slice(0, 5) ?? [];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--color-text)]">
          Добро пожаловать{user?.email ? `, ${user.email.split('@')[0]}` : ''}
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">Вот что происходит с вашими интервью</p>
      </div>

      {isLoading ? (
        <PageLoader />
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard label="Планов" value={stats.totalPlans} sub={`${stats.publishedPlans} опубликовано`} />
            <StatCard label="Интервью" value={stats.totalInterviews} sub={`${stats.completedInterviews} завершено`} />
            <StatCard label="В процессе" value={interviews?.filter((i) => i.status === 'in_progress').length ?? 0} />
            <StatCard label="Черновики" value={plans?.filter((p) => p.status === 'draft').length ?? 0} sub="планов" />
          </div>

          {/* Quick actions */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <Link href="/plans">
              <Card hoverable className="flex items-center gap-4 py-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--color-gold)]/10 flex items-center justify-center shrink-0">
                  <svg className="w-5 h-5 text-[var(--color-gold)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--color-text)]">Управление планами</p>
                  <p className="text-xs text-[var(--color-text-muted)]">Создать или редактировать</p>
                </div>
              </Card>
            </Link>
            <Link href="/interviews">
              <Card hoverable className="flex items-center gap-4 py-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--color-info)]/10 flex items-center justify-center shrink-0">
                  <svg className="w-5 h-5 text-[var(--color-info)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--color-text)]">Интервью</p>
                  <p className="text-xs text-[var(--color-text-muted)]">Начать или просмотреть</p>
                </div>
              </Card>
            </Link>
          </div>

          {/* Recent interviews */}
          {recentInterviews.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-[var(--color-text)]">Последние интервью</h2>
                <Link href="/interviews">
                  <Button variant="ghost" size="sm">Все интервью →</Button>
                </Link>
              </div>
              <div className="flex flex-col gap-2">
                {recentInterviews.map((interview) => (
                  <Link key={interview.id} href={`/interviews/${interview.id}`}>
                    <Card hoverable className="flex items-center justify-between py-3">
                      <div>
                        <p className="text-sm font-medium text-[var(--color-text)]">{interview.candidate_name}</p>
                        <p className="text-xs text-[var(--color-text-muted)]">{interview.type} · План #{interview.plan_id}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-[var(--color-text-subtle)]">{interview.answers.length} ответов</span>
                        <Badge value={interview.status} />
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
