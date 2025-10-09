'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useLocale } from 'next-intl';
import { useTransition } from 'react';

const locales = [
  { code: 'pt-br', name: 'Português (BR)', flag: '/flags/br.svg' },
  { code: 'en', name: 'English', flag: '/flags/us.svg' },
];

interface LanguageSwitcherButtonProps {
  className?: string;
  variant?: 'dropdown' | 'toggle';
}

export default function LanguageSwitcherButton({
  className = '',
  variant = 'dropdown',
}: LanguageSwitcherButtonProps) {
  const [isPending, startTransition] = useTransition();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLanguageChange = (newLocale: string) => {
    startTransition(() => {
      // Remove the current locale from pathname and add the new one
      const newPathname = pathname.replace(`/${locale}`, `/${newLocale}`);
      router.push(newPathname);
    });
  };

  if (variant === 'toggle') {
    const otherLocale = locale === 'pt-br' ? 'en' : 'pt-br';
    const otherLocaleData = locales.find((l) => l.code === otherLocale);

    return (
      <button
        onClick={() => handleLanguageChange(otherLocale)}
        disabled={isPending}
        className={`inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        title={`Switch to ${otherLocaleData?.name}`}
      >
        <span className="text-lg">{otherLocale === 'pt-br' ? '🇧🇷' : '🇺🇸'}</span>
        <span className="hidden sm:inline">{otherLocaleData?.name}</span>
      </button>
    );
  }

  return (
    <div className={`relative inline-block text-left ${className}`}>
      <select
        className="appearance-none bg-white border border-gray-300 rounded-md py-2 pl-3 pr-8 text-sm leading-5 text-gray-700 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        value={locale}
        onChange={(e) => handleLanguageChange(e.target.value)}
        disabled={isPending}
      >
        {locales.map((loc) => (
          <option key={loc.code} value={loc.code}>
            {loc.code === 'pt-br' ? '🇧🇷' : '🇺🇸'} {loc.name}
          </option>
        ))}
      </select>

      {/* Custom dropdown arrow */}
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
        <svg
          className="fill-current h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
        >
          <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
        </svg>
      </div>
    </div>
  );
}
