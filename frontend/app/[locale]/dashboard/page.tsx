'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';

interface Optimization {
  id: string;
  resume_name: string;
  job_title: string;
  company: string;
  status: 'processing' | 'completed' | 'failed';
  match_score?: number;
  created_at: string;
  optimized_resume_url?: string;
}

interface UserStats {
  optimizations_used: number;
  free_optimizations_limit: number;
  free_optimizations_used: number;
  purchased_optimizations: number;
  success_rate: number;
  avg_match_score: number;
  total_applications: number;
}

function DashboardContent() {
  const { user, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [optimizations, setOptimizations] = useState<Optimization[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const router = useRouter();
  const t = useTranslations('dashboard.dashboard');
  const tCommon = useTranslations('common');

  useEffect(() => {
    async function loadDashboardData() {
      if (!user) return;

      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Load user's credits from API
        const creditsResponse = await fetch(`${API_URL}/api/optimizations/credits/check`, {
          credentials: 'include',
        });

        let creditsData = {
          credits: 0,
          free_used: 0,
          free_limit: 3,
          purchased: 0,
        };
        if (creditsResponse.ok) {
          creditsData = await creditsResponse.json();
        }

        // Mock data for optimizations
        setOptimizations([
          {
            id: '1',
            resume_name: 'Software_Engineer_Resume.pdf',
            job_title: 'Senior Software Engineer',
            company: 'Tech Company',
            status: 'completed',
            match_score: 85,
            created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            optimized_resume_url: '/mock-download',
          },
          {
            id: '2',
            resume_name: 'Frontend_Dev_Resume.docx',
            job_title: 'Frontend Developer',
            company: 'StartupXYZ',
            status: 'processing',
            created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          },
        ]);

        // Update stats with real credit data
        const totalCredits = creditsData.credits || 0;
        const freeUsed = creditsData.free_used || 0;
        const freeLimit = creditsData.free_limit || 3;
        const purchased = creditsData.purchased || 0;

        setStats({
          optimizations_used: freeUsed + (purchased - (totalCredits - (freeLimit - freeUsed))),
          free_optimizations_limit: freeLimit,
          free_optimizations_used: freeUsed,
          purchased_optimizations: totalCredits - (freeLimit - freeUsed),
          success_rate: 95,
          avg_match_score: 82,
          total_applications: 5,
        });
      } catch (error) {
        // TODO: Implement proper error logging service

        // Fallback to mock data
        setOptimizations([
          {
            id: '1',
            resume_name: 'Software_Engineer_Resume.pdf',
            job_title: 'Senior Software Engineer',
            company: 'Tech Company',
            status: 'completed',
            match_score: 85,
            created_at: new Date(Date.now() - 86400000).toISOString(),
            optimized_resume_url: '/mock-download',
          },
        ]);

        setStats({
          optimizations_used: 2,
          free_optimizations_limit: 3,
          free_optimizations_used: 2,
          purchased_optimizations: 0,
          success_rate: 95,
          avg_match_score: 82,
          total_applications: 5,
        });
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboardData();
  }, [user]);

  const handleSignOut = () => {
    logout();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">{tCommon('ui.loading')}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="font-bold text-2xl text-blue-600">
              CV-Match
            </Link>

            {user && (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  {t('welcome.title', {
                    name: user.email?.split('@')[0] || 'User',
                  })}
                </span>
                <Button variant="outline" size="sm" onClick={() => router.push('/settings')}>
                  {tCommon('navigation.profile')}
                </Button>
                <Button variant="ghost" size="sm" onClick={handleSignOut}>
                  {tCommon('navigation.logout')}
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('title')}</h1>
          <p className="text-gray-600">{t('subtitle')}</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => router.push('/optimize')}
          >
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">{t('overview.quickActions.title')}</h3>
                  <p className="text-sm text-gray-600">
                    {t('overview.quickActions.newOptimization')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => router.push('/results')}
          >
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">{t('optimizations.title')}</h3>
                  <p className="text-sm text-gray-600">
                    {t('overview.quickActions.viewTemplates')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => router.push('/settings')}
          >
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-purple-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">{t('settings.title')}</h3>
                  <p className="text-sm text-gray-600">{t('overview.quickActions.upgradePlan')}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Statistics and Credits */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Statistics Card */}
            <Card>
              <CardHeader>
                <CardTitle>{t('overview.title')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {stats.optimizations_used}
                    </div>
                    <div className="text-sm text-gray-600">
                      {t('overview.stats.totalOptimizations')}
                    </div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{stats.success_rate}%</div>
                    <div className="text-sm text-gray-600">{t('overview.stats.successRate')}</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {stats.avg_match_score}%
                    </div>
                    <div className="text-sm text-gray-600">
                      {t('analytics.performance.averageScore')}
                    </div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {stats.total_applications}
                    </div>
                    <div className="text-sm text-gray-600">{t('overview.stats.activeResumes')}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Credits Card */}
            <Card>
              <CardHeader>
                <CardTitle>{t('credits.title')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Total Available Credits */}
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600">
                      {stats.free_optimizations_limit -
                        stats.free_optimizations_used +
                        stats.purchased_optimizations}
                    </div>
                    <div className="text-sm text-gray-600">créditos disponíveis</div>
                  </div>

                  {/* Credit Breakdown */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{t('credits.freeUsed')}</span>
                      <span className="font-medium">
                        {stats.free_optimizations_used} / {stats.free_optimizations_limit}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{
                          width: `${(stats.free_optimizations_used / stats.free_optimizations_limit) * 100}%`,
                        }}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{t('credits.purchased')}</span>
                      <span className="font-medium">{stats.purchased_optimizations}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="pt-4 space-y-2">
                    <Button className="w-full" onClick={() => router.push('/pricing')}>
                      {t('credits.buyMore')}
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => router.push('/optimize')}
                    >
                      Usar Crédito
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recent Optimizations */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{t('recentOptimizations.title')}</CardTitle>
              <CardDescription>Your latest resume optimization activities</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => router.push('/history')}>
              {t('recentOptimizations.viewAll')}
            </Button>
          </CardHeader>
          <CardContent>
            {optimizations.length === 0 ? (
              <div className="text-center py-8">
                <svg
                  className="w-12 h-12 text-gray-400 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p className="text-gray-600 mb-4">{t('recentOptimizations.noOptimizations')}</p>
                <Button onClick={() => router.push('/optimize')}>{t('optimizeResume')}</Button>
              </div>
            ) : (
              <div className="space-y-4">
                {optimizations.map((optimization) => (
                  <div
                    key={optimization.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-medium">{optimization.resume_name}</h4>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(optimization.status)}`}
                        >
                          {t(`recentOptimizations.status.${optimization.status}`)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {optimization.job_title} at {optimization.company} •{' '}
                        {formatDate(optimization.created_at)}
                      </p>
                      {optimization.match_score && (
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${optimization.match_score}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-green-600">
                            {optimization.match_score}%
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {optimization.status === 'completed' && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => router.push(`/results/${optimization.id}`)}
                          >
                            {t('recentOptimizations.actions.view')}
                          </Button>
                          <Button size="sm">{t('recentOptimizations.actions.download')}</Button>
                        </>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => router.push('/optimize')}>
                        {t('recentOptimizations.actions.optimize')}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
