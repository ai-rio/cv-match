'use client';

import { BarChart3, FileText, Home, Settings, TrendingUp, User } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: ReactNode;
  className?: string;
}

const sidebarNavigation = [
  {
    name: 'Visão Geral',
    href: '/dashboard',
    icon: Home,
  },
  {
    name: 'Meus Currículos',
    href: '/dashboard/resumes',
    icon: FileText,
  },
  {
    name: 'Análises',
    href: '/dashboard/analysis',
    icon: BarChart3,
  },
  {
    name: 'Estatísticas',
    href: '/dashboard/statistics',
    icon: TrendingUp,
  },
  {
    name: 'Perfil',
    href: '/dashboard/profile',
    icon: User,
  },
  {
    name: 'Configurações',
    href: '/dashboard/settings',
    icon: Settings,
  },
];

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  return (
    <div className={cn('flex h-screen bg-background', className)}>
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0">
        <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-card border-r">
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">CV</span>
              </div>
              <span className="font-bold text-lg">CV-Match</span>
            </Link>
          </div>
          <nav className="mt-8 flex-1 px-4 space-y-1">
            {sidebarNavigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive(item.href)
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  )}
                >
                  <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="flex-shrink-0 flex border-t p-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <span className="text-primary-foreground text-sm font-medium">U</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">Usuário</p>
                <p className="text-xs text-muted-foreground truncate">usuario@exemplo.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64 flex flex-col flex-1">
        {/* Mobile header */}
        <div className="md:hidden sticky top-0 z-10 bg-card border-b">
          <div className="flex items-center justify-between px-4 py-3">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="h-7 w-7 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-xs">CV</span>
              </div>
              <span className="font-bold">CV-Match</span>
            </Link>
            <Button variant="ghost" size="sm">
              Menu
            </Button>
          </div>
        </div>

        {/* Main content area */}
        <main className="flex-1 overflow-y-auto">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
}
