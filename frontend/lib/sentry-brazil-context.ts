/**
 * Brazilian Market Context for Sentry
 *
 * This utility provides Brazilian market-specific context and localization
 * for Sentry error tracking and performance monitoring in CV-Match.
 */

import * as Sentry from '@sentry/nextjs';

export interface BrazilianUserContext {
  id: string;
  email?: string;
  name?: string;
  locale?: 'pt-BR' | 'en';
  currency?: 'BRL' | 'USD' | 'EUR';
  plan?: 'free' | 'basic' | 'premium' | 'enterprise';
  subscriptionStatus?: 'active' | 'trialing' | 'canceled' | 'past_due';
}

export interface BrazilianTransactionContext {
  transactionName: string;
  operation: string;
  currency?: string;
  amount?: number;
  paymentMethod?: 'credit_card' | 'pix' | 'boleto';
  success?: boolean;
}

/**
 * Brazilian Market Context Manager for Sentry
 */
export class SentryBrazilianContext {
  private static instance: SentryBrazilianContext;

  static getInstance(): SentryBrazilianContext {
    if (!SentryBrazilianContext.instance) {
      SentryBrazilianContext.instance = new SentryBrazilianContext();
    }
    return SentryBrazilianContext.instance;
  }

  /**
   * Set user context with Brazilian market information
   */
  setUserContext(user: BrazilianUserContext): void {
    const context = {
      id: user.id,
      email: user.email,
      username: user.name,
      // Brazilian-specific context
      locale: user.locale || 'pt-BR',
      market: 'brazil',
      currency: user.currency || 'BRL',
      country: 'BR',
      timezone: 'America/Sao_Paulo',
      // Plan and subscription context
      plan: user.plan,
      subscription_status: user.subscriptionStatus,
      // Additional context
      region: 'latam',
      saas_type: 'resume-matching',
      industry: 'HR_Tech',
    };

    Sentry.setUser(context);
    this.addBreadcrumb('User context set', 'user', 'info');
  }

  /**
   * Set transaction context with Brazilian business logic
   */
  setTransactionContext(transaction: BrazilianTransactionContext): void {
    Sentry.setTag('transaction_type', transaction.operation);
    Sentry.setTag('currency', transaction.currency || 'BRL');
    Sentry.setTag('payment_method', transaction.paymentMethod);
    Sentry.setTag('market', 'brazil');

    Sentry.setExtra('transaction_context', {
      ...transaction,
      market: 'brazil',
      locale: 'pt-BR',
      country: 'BR',
      timezone: 'America/Sao_Paulo',
    });

    // Note: setTransactionName is deprecated in newer Sentry versions
    // Transaction naming is handled automatically
  }

  /**
   * Add Brazilian market breadcrumb
   */
  addBreadcrumb(
    message: string,
    category: string = 'brazil-context',
    level: Sentry.SeverityLevel = 'info',
    data?: Record<string, unknown>
  ): void {
    Sentry.addBreadcrumb({
      message,
      category,
      level,
      data: {
        ...data,
        market: 'brazil',
        locale: 'pt-BR',
        country: 'BR',
        currency: 'BRL',
        timezone: 'America/Sao_Paulo',
      },
    });
  }

  /**
   * Capture exception with Brazilian context
   */
  captureException(
    error: Error,
    context?: {
      operation?: string;
      feature?: string;
      userAction?: string;
      paymentContext?: {
        method?: string;
        amount?: number;
        currency?: string;
      };
    }
  ): void {
    const extraContext = {
      market: 'brazil',
      locale: 'pt-BR',
      country: 'BR',
      currency: 'BRL',
      application: 'cv-match-frontend',
      ...context,
    };

    // Localize error messages for common Brazilian scenarios
    let localizedMessage = error.message;
    if (context) {
      localizedMessage = this.localizeErrorMessage(error.message, context);
    }

    Sentry.captureException(error, {
      extra: extraContext,
      tags: {
        market: 'brazil',
        locale: 'pt-BR',
        currency: 'BRL',
        operation: context?.operation,
        feature: context?.feature,
        user_action: context?.userAction,
      },
    });

    this.addBreadcrumb(`Exception captured: ${localizedMessage}`, 'error', 'error', {
      error_type: error.constructor.name,
      localized_message: localizedMessage,
    });
  }

  /**
   * Capture message with Brazilian context
   */
  captureMessage(
    message: string,
    level: Sentry.SeverityLevel = 'info',
    context?: Record<string, unknown>
  ): void {
    const localizedMessage = this.localizeMessage(message);

    Sentry.captureMessage(localizedMessage, {
      level,
      extra: {
        market: 'brazil',
        locale: 'pt-BR',
        country: 'BR',
        currency: 'BRL',
        application: 'cv-match-frontend',
        ...context,
      },
      tags: {
        market: 'brazil',
        locale: 'pt-BR',
        currency: 'BRL',
      },
    });

    this.addBreadcrumb(`Message captured: ${localizedMessage}`, 'message', level, {
      original_message: message,
      localized_message: localizedMessage,
    });
  }

  /**
   * Set Brazilian market tags
   */
  setBrazilianTags(tags: {
    feature?: string;
    operation?: string;
    paymentFlow?: string;
    userPlan?: string;
    subscriptionStatus?: string;
  }): void {
    Sentry.setTag('market', 'brazil');
    Sentry.setTag('locale', 'pt-BR');
    Sentry.setTag('country', 'BR');
    Sentry.setTag('currency', 'BRL');
    Sentry.setTag('region', 'latam');
    Sentry.setTag('saas_type', 'resume-matching');
    Sentry.setTag('industry', 'HR_Tech');

    // Set custom tags
    Object.entries(tags).forEach(([key, value]) => {
      if (value) {
        Sentry.setTag(key, value);
      }
    });
  }

  /**
   * Add Brazilian business context
   */
  addBusinessContext(context: {
    businessOperation?: string;
    revenueImpact?: 'high' | 'medium' | 'low';
    userImpact?: 'critical' | 'high' | 'medium' | 'low';
    compliance?: 'LGPD' | 'PCI-DSS' | 'GDPR';
  }): void {
    Sentry.setExtra('business_context', {
      ...context,
      market: 'brazil',
      locale: 'pt-BR',
      country: 'BR',
      currency: 'BRL',
      timezone: 'America/Sao_Paulo',
    });

    if (context.compliance) {
      Sentry.setTag('compliance', context.compliance);
    }
  }

  /**
   * Localize error messages for Brazilian market
   */
  private localizeErrorMessage(
    message: string,
    context: {
      operation?: string;
      feature?: string;
      userAction?: string;
      paymentContext?: {
        method?: string;
        amount?: number;
        currency?: string;
      };
    }
  ): string {
    const lowerMessage = message.toLowerCase();

    // Payment-related errors
    if (context.paymentContext) {
      if (lowerMessage.includes('payment failed')) {
        return 'Falha no processamento do pagamento. Tente novamente ou use outro método.';
      }
      if (lowerMessage.includes('card declined')) {
        return 'Cartão recusado. Verifique os dados ou use outro cartão.';
      }
      if (lowerMessage.includes('insufficient funds')) {
        return 'Saldo insuficiente. Verifique seu saldo ou use outra forma de pagamento.';
      }
    }

    // Validation errors
    if (lowerMessage.includes('email invalid')) {
      return 'E-mail inválido. Verifique o endereço digitado.';
    }
    if (lowerMessage.includes('cpf invalid')) {
      return 'CPF inválido. Verifique os números digitados.';
    }
    if (lowerMessage.includes('cnpj invalid')) {
      return 'CNPJ inválido. Verifique os números digitados.';
    }

    // General errors
    if (lowerMessage.includes('network error')) {
      return 'Erro de conexão. Verifique sua internet e tente novamente.';
    }
    if (lowerMessage.includes('timeout')) {
      return 'Tempo esgotado. Tente novamente mais tarde.';
    }

    return message;
  }

  /**
   * Localize general messages
   */
  private localizeMessage(message: string): string {
    const lowerMessage = message.toLowerCase();

    // Common Portuguese translations
    const translations: Record<string, string> = {
      'user logged in': 'Usuário logado com sucesso',
      'user logged out': 'Usuário deslogado',
      'payment successful': 'Pagamento realizado com sucesso',
      'payment failed': 'Falha no pagamento',
      'subscription created': 'Assinatura criada com sucesso',
      'subscription cancelled': 'Assinatura cancelada',
      'resume uploaded': 'Currículo enviado com sucesso',
      'resume processed': 'Currículo processado com sucesso',
      'job matched': 'Vaga compatível encontrada',
      'profile updated': 'Perfil atualizado com sucesso',
    };

    for (const [english, portuguese] of Object.entries(translations)) {
      if (lowerMessage.includes(english)) {
        return portuguese;
      }
    }

    return message;
  }

  /**
   * Clear user context (for logout)
   */
  clearUserContext(): void {
    Sentry.setUser(null);
    this.addBreadcrumb('User context cleared', 'auth', 'info');
  }
}

// Export singleton instance
export const sentryBrazil = SentryBrazilianContext.getInstance();

// Export convenience functions
export const setBrazilianUserContext = (user: BrazilianUserContext) =>
  sentryBrazil.setUserContext(user);

export const setBrazilianTransactionContext = (transaction: BrazilianTransactionContext) =>
  sentryBrazil.setTransactionContext(transaction);

export const captureBrazilianException = (
  error: Error,
  context?: {
    operation?: string;
    feature?: string;
    userAction?: string;
    paymentContext?: {
      method?: string;
      amount?: number;
      currency?: string;
    };
  }
) => sentryBrazil.captureException(error, context);

export const captureBrazilianMessage = (
  message: string,
  level?: Sentry.SeverityLevel,
  context?: Record<string, unknown>
) => sentryBrazil.captureMessage(message, level, context);

export const addBrazilianBreadcrumb = (
  message: string,
  category?: string,
  level?: Sentry.SeverityLevel,
  data?: Record<string, unknown>
) => sentryBrazil.addBreadcrumb(message, category, level, data);

export const setBrazilianTags = (tags: {
  feature?: string;
  operation?: string;
  paymentFlow?: string;
  userPlan?: string;
  subscriptionStatus?: string;
}) => sentryBrazil.setBrazilianTags(tags);
