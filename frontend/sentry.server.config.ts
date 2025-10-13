// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

// Get environment variables
const dsn =
  process.env.SENTRY_DSN ||
  'https://22998f07e8a5984c30aabe3b89b0af4c@o4510150793232384.ingest.us.sentry.io/4510150794412032';
const environment = process.env.SENTRY_ENVIRONMENT || process.env.NODE_ENV || 'development';
const tracesSampleRate = parseFloat(process.env.SENTRY_TRACES_SAMPLE_RATE || '1.0');

Sentry.init({
  dsn: dsn,

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: tracesSampleRate,

  // Enable logs to be sent to Sentry
  enableLogs: true,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: environment === 'development',

  // Add Brazilian market context
  environment: environment,

  // Custom tags for Brazilian SaaS context
  beforeSend(event) {
    // Add Brazilian market tags
    event.tags = {
      ...event.tags,
      market: 'brazil',
      currency: 'BRL',
      locale: 'pt-BR',
      region: 'latam',
      saas_type: 'resume-matching',
      application: 'cv-match-frontend',
    };

    // Add custom context for Brazilian business logic
    event.extra = {
      ...event.extra,
      market_context: {
        country: 'BR',
        currency: 'BRL',
        language: 'pt-BR',
        timezone: 'America/Sao_Paulo',
        business_model: 'SaaS',
        industry: 'HR_Tech',
      },
    };

    return event;
  },

  // Set release version
  release: process.env.APP_VERSION || 'cv-match@1.0.0',

  // Performance monitoring settings
  sendDefaultPii: false, // Privacy compliance for LGPD
});
