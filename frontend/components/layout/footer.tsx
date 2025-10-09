'use client';

import { Github, Linkedin, Mail, Twitter } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';

interface FooterProps {
  className?: string;
}

export function Footer({ className }: FooterProps) {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { name: 'Recursos', href: '/features' },
      { name: 'Preços', href: '/pricing' },
      { name: 'Cases de Sucesso', href: '/testimonials' },
      { name: 'API', href: '/api' },
    ],
    company: [
      { name: 'Sobre Nós', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Carreiras', href: '/careers' },
      { name: 'Contato', href: '/contact' },
    ],
    resources: [
      { name: 'Central de Ajuda', href: '/help' },
      { name: 'Documentação', href: '/docs' },
      { name: 'Guias', href: '/guides' },
      { name: 'Webinars', href: '/webinars' },
    ],
    legal: [
      { name: 'Política de Privacidade', href: '/privacy' },
      { name: 'Termos de Serviço', href: '/terms' },
      { name: 'LGPD', href: '/lgpd' },
      { name: 'Cookies', href: '/cookies' },
    ],
  };

  const socialLinks = [
    { name: 'Twitter', href: '#', icon: Twitter },
    { name: 'LinkedIn', href: '#', icon: Linkedin },
    { name: 'GitHub', href: '#', icon: Github },
    { name: 'Email', href: 'mailto:contato@cv-match.com.br', icon: Mail },
  ];

  return (
    <footer className={className}>
      <div className="container px-4 py-12">
        {/* Main footer content */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-5">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <Link href="/" className="inline-flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">CV</span>
              </div>
              <span className="font-bold text-xl">CV-Match</span>
            </Link>
            <p className="mt-4 text-sm text-muted-foreground max-w-xs">
              Potencialize sua carreira com IA. Analisamos seu currículo e encontramos as vagas
              perfeitas para você.
            </p>
            <div className="mt-6 flex space-x-4">
              {socialLinks.map((item) => {
                const Icon = item.icon;
                return (
                  <Button key={item.name} variant="ghost" size="icon" asChild className="h-8 w-8">
                    <Link href={item.href} aria-label={item.name}>
                      <Icon className="h-4 w-4" />
                    </Link>
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Links columns */}
          <div className="grid grid-cols-2 gap-8 lg:col-span-4 sm:grid-cols-4">
            <div>
              <h3 className="text-sm font-semibold">Produto</h3>
              <ul className="mt-4 space-y-3">
                {footerLinks.product.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold">Empresa</h3>
              <ul className="mt-4 space-y-3">
                {footerLinks.company.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold">Recursos</h3>
              <ul className="mt-4 space-y-3">
                {footerLinks.resources.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold">Legal</h3>
              <ul className="mt-4 space-y-3">
                {footerLinks.legal.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-12 border-t pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 md:flex-row">
            <p className="text-sm text-muted-foreground">
              © {currentYear} CV-Match. Todos os direitos reservados.
            </p>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">Feito com ❤️ no Brasil</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
