'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';

import LanguageSwitcher from './LanguageSwitcher';

export default function Navigation() {
  const t = useTranslations('common');
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path || pathname.startsWith(path + '/');
  };

  const navLinks = [
    { href: '/', label: t('navigation.home') },
    { href: '/dashboard', label: t('navigation.dashboard') },
    { href: '/pricing', label: t('navigation.pricing') },
    { href: '/blog', label: t('navigation.blog') },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-xl font-bold text-gray-900">
              CV-Match
            </Link>
          </div>

          {/* Main Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive(link.href)
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right side items */}
          <div className="flex items-center space-x-4">
            <LanguageSwitcher />

            <Link
              href="/login"
              className="text-sm font-medium text-gray-700 hover:text-primary-600"
            >
              {t('navigation.login')}
            </Link>

            <Link
              href="/signup"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {t('navigation.signup')}
            </Link>
          </div>
        </div>
      </div>

      {/* Mobile menu - Language switcher for mobile */}
      <div className="md:hidden border-t border-gray-200 px-4 py-2">
        <div className="flex justify-between items-center">
          <div className="flex space-x-2">
            {navLinks.slice(0, 3).map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                  isActive(link.href)
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-primary-600'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <LanguageSwitcher />
        </div>
      </div>
    </nav>
  );
}
