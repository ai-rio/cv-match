'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';

import { SubscriptionDashboard } from '@/components/account/SubscriptionDashboard';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/contexts/AuthContext';

export default function SettingsPage() {
  const t = useTranslations('dashboard');
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setSaveStatus('idle');

    try {
      // TODO: Implement actual profile save logic
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSaveStatus('success');
    } catch {
      setSaveStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setSaveStatus('idle');

    try {
      // TODO: Implement actual preferences save logic
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSaveStatus('success');
    } catch {
      setSaveStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">{t('settings.title')}</h1>
            <p className="mt-2 text-gray-600">{t('settings.subtitle')}</p>
          </div>

          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">{t('settings.profile.title')}</TabsTrigger>
              <TabsTrigger value="preferences">{t('settings.preferences.title')}</TabsTrigger>
              <TabsTrigger value="privacy">{t('settings.privacy.title')}</TabsTrigger>
              <TabsTrigger value="billing">{t('billing.title')}</TabsTrigger>
            </TabsList>

            {/* Profile Tab */}
            <TabsContent value="profile">
              <Card>
                <CardHeader>
                  <CardTitle>{t('settings.profile.title')}</CardTitle>
                  <CardDescription>Update your personal information</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSaveProfile} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="firstName">{t('auth.firstName')}</Label>
                        <Input
                          id="firstName"
                          type="text"
                          placeholder={t('auth.firstNamePlaceholder')}
                          defaultValue={user?.user_metadata?.first_name || ''}
                        />
                      </div>
                      <div>
                        <Label htmlFor="lastName">{t('auth.lastName')}</Label>
                        <Input
                          id="lastName"
                          type="text"
                          placeholder={t('auth.lastNamePlaceholder')}
                          defaultValue={user?.user_metadata?.last_name || ''}
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="email">{t('auth.email')}</Label>
                      <Input id="email" type="email" value={user?.email || ''} disabled />
                      <p className="text-sm text-gray-500 mt-1">
                        Email cannot be changed. Contact support if needed.
                      </p>
                    </div>
                    <div>
                      <Label htmlFor="bio">{t('settings.profile.bio')}</Label>
                      <textarea
                        id="bio"
                        className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                        rows={4}
                        placeholder="Tell us about yourself..."
                        defaultValue={user?.user_metadata?.bio || ''}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        {saveStatus === 'success' && (
                          <p className="text-sm text-green-600">{t('settings.profile.success')}</p>
                        )}
                        {saveStatus === 'error' && (
                          <p className="text-sm text-red-600">Error saving profile</p>
                        )}
                      </div>
                      <Button type="submit" disabled={isLoading}>
                        {isLoading ? t('settings.profile.saving') : t('settings.profile.save')}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Preferences Tab */}
            <TabsContent value="preferences">
              <Card>
                <CardHeader>
                  <CardTitle>{t('settings.preferences.title')}</CardTitle>
                  <CardDescription>Manage your application preferences</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSavePreferences} className="space-y-6">
                    <div>
                      <Label htmlFor="language">{t('settings.preferences.language')}</Label>
                      <select
                        id="language"
                        className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                        defaultValue="pt-br"
                      >
                        <option value="pt-br">Português (Brasil)</option>
                        <option value="en">English</option>
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="timezone">{t('settings.preferences.timezone')}</Label>
                      <select
                        id="timezone"
                        className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                        defaultValue="America/Sao_Paulo"
                      >
                        <option value="America/Sao_Paulo">America/São Paulo (BRT)</option>
                        <option value="America/New_York">America/New York (EST)</option>
                        <option value="Europe/London">Europe/London (GMT)</option>
                      </select>
                    </div>
                    <div>
                      <Label className="text-base font-medium">
                        {t('settings.preferences.notifications')}
                      </Label>
                      <div className="mt-3 space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{t('settings.preferences.email')}</div>
                            <div className="text-sm text-gray-500">
                              Receive email updates about your optimizations
                            </div>
                          </div>
                          <input type="checkbox" defaultChecked className="h-4 w-4" />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{t('settings.preferences.push')}</div>
                            <div className="text-sm text-gray-500">
                              Push notifications for completed optimizations
                            </div>
                          </div>
                          <input type="checkbox" defaultChecked className="h-4 w-4" />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{t('settings.preferences.marketing')}</div>
                            <div className="text-sm text-gray-500">
                              Promotional offers and new features
                            </div>
                          </div>
                          <input type="checkbox" className="h-4 w-4" />
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        {saveStatus === 'success' && (
                          <p className="text-sm text-green-600">
                            {t('settings.preferences.success')}
                          </p>
                        )}
                        {saveStatus === 'error' && (
                          <p className="text-sm text-red-600">Error saving preferences</p>
                        )}
                      </div>
                      <Button type="submit" disabled={isLoading}>
                        {isLoading ? t('common.ui.loading') : t('settings.preferences.save')}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Privacy Tab */}
            <TabsContent value="privacy">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>{t('settings.privacy.title')}</CardTitle>
                    <CardDescription>Manage your privacy and security settings</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button variant="outline" className="w-full justify-start">
                      {t('settings.privacy.changePassword')}
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      {t('settings.privacy.twoFactor')}
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      {t('settings.privacy.dataExport')}
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-red-600 hover:text-red-700"
                    >
                      {t('settings.privacy.deleteAccount')}
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>LGPD Compliance</CardTitle>
                    <CardDescription>
                      Your data protection rights under Brazilian law
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        LGPD Compliant
                      </Badge>
                      <p className="text-sm text-gray-600">
                        We comply with the Brazilian General Data Protection Law (LGPD). You have
                        the right to access, correct, delete, and export your personal data.
                      </p>
                      <Button variant="outline" size="sm">
                        Learn more about LGPD
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Billing Tab */}
            <TabsContent value="billing">
              <div className="space-y-6">
                <SubscriptionDashboard />

                <Card>
                  <CardHeader>
                    <CardTitle>{t('billing.paymentMethods')}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">No payment methods on file</p>
                    <Button variant="outline" className="mt-4">
                      Add Payment Method
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>{t('billing.invoices')}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">No invoices yet</p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </ProtectedRoute>
  );
}
