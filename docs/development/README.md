# Development Documentation

**Quick Start**: See [ROADMAP.md](./ROADMAP.md) for prioritized implementation plan.

## 📍 Current Status

**Phase**: Migration from Resume-Matcher to cv-match
**Timeline**: 4-week sprint to production launch
**Next Action**: P0 backend services migration (Week 1)

## 🗂️ Documentation Index

### 🎯 Planning & Strategy
- **[ROADMAP.md](./ROADMAP.md)** - Prioritized implementation plan (P0/P1/P2 tiers)
  - 4-week timeline with weekly milestones
  - Gap analysis: Resume-Matcher vs cv-match
  - Success metrics and risk mitigation

- **[Business Model Analysis](./business-model-analysis.md)** - Monetization strategy
  - Credit-based vs subscription comparison
  - Brazilian market pricing (R$ 49.90/month, R$ 297 lifetime)
  - Financial projections (R$ 20M+ valuation by Year 3)

### 🔧 Integration Guides
- **[Resume-Matcher Integration Strategy](./resume-matcher-integration.md)**
  - Complete codebase analysis
  - Time savings breakdown (90% reduction)
  - Component inventory

- **[Implementation Guide](./implementation-guide.md)**
  - Step-by-step migration instructions
  - Database migration scripts
  - Testing procedures

- **[Architecture Overview](./architecture-overview.md)**
  - System architecture diagrams
  - Technology stack details
  - Security and scalability

### 🌎 Brazilian Market
- **[Next-Intl Integration](./next-intl-integration.md)**
  - PT-BR internationalization setup
  - Translation infrastructure
  - Cultural adaptations

- **[Stripe Integration Analysis](./stripe-integration-analysis.md)**
  - BRL payment configuration
  - Webhook security and idempotency
  - Brazilian payment methods (PIX, Boleto)

## 🚀 Quick Commands

### Development
```bash
# Start full stack
make dev

# Backend only
make dev-backend

# Frontend only
make dev-frontend

# Install dependencies
make install-frontend  # Uses Bun
make install-backend   # Uses uv
```

### Database
```bash
# Create migration
make db-migration-new name=description

# Apply migrations
supabase db push

# Check status
make db-status
```

### Testing
```bash
# Backend tests
cd backend && python -m pytest

# Frontend dev server
cd frontend && bun dev
```

## 📊 Progress Tracking

### Week 1: Backend Foundation (P0)
- [ ] Copy resume processing services
- [ ] Copy agent system
- [ ] Apply database migrations
- [ ] Create API endpoints

### Week 2: Frontend & i18n (P0)
- [ ] Copy optimization pages
- [ ] Copy UI components
- [ ] Install next-intl
- [ ] Copy PT-BR translations

### Week 3: Payments (P1)
- [ ] Copy Stripe services
- [ ] Copy payment pages
- [ ] Set up webhooks
- [ ] Integrate usage tracking

### Week 4: Polish & Launch (P1)
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Production deployment
- [ ] Beta user launch

## 🎓 Learning Resources

### Source Code
- **Resume-Matcher**: `/home/carlos/projects/Resume-Matcher/apps/`
  - Backend: `backend/app/services/` (13 services, ~3,264 LOC)
  - Frontend: `frontend/app/` (30+ pages)
  - i18n: `frontend/locales/` (PT-BR + EN)

### Environment Setup
- **Backend**: Python 3.12+, FastAPI, Supabase
- **Frontend**: Node 18+, Next.js 15, Bun, next-intl v4.3.6
- **Database**: Local Supabase with RLS

### Key Dependencies
```bash
# Backend
openai>=1.0.0
anthropic>=0.21.0
stripe>=5.0.0
supabase>=2.0.0

# Frontend
next-intl@4.3.6
@stripe/stripe-js
@supabase/supabase-js
```

## 🔗 External Resources

- **Supabase Docs**: https://supabase.com/docs
- **Next-Intl Docs**: https://next-intl-docs.vercel.app
- **Stripe Docs**: https://stripe.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs

## 📞 Support

### Common Issues
- **Import Errors**: Check Python path and dependencies
- **Database Errors**: Verify Supabase connection and migrations
- **Auth Issues**: Check Supabase auth configuration
- **i18n Issues**: Verify next-intl middleware setup
- **Payment Issues**: Check Stripe webhook configuration

### Debug Mode
```bash
LOG_LEVEL=DEBUG
RESUME_MATCHER_DEBUG=true
```

---

**Last Updated**: 2025-10-07
**Status**: Active Development
**Next Review**: After Week 1 completion
