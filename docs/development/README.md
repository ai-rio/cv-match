# Development Documentation

This directory contains all development documentation for the CV-Match project, now organized by category.

## 📁 Folder Structure

### Organized Documentation

- **01-security/** - Security audits, fixes, and implementation docs
- **02-phase-management/** - Phase 0, 1, and 1.5 documentation
- **03-reports-audits/** - Progress reports and code audits
- **04-guides/** - Implementation guides and quick-starts
- **05-architecture/** - System architecture and business models
- **06-dependencies/** - Dependency management documentation
- **07-integrations/** - Third-party integration docs (Stripe, Next-intl, etc.)
- **08-assets/** - Static assets (CSS, images, etc.)

### Specialized Directories

- **UI-UX/** - User interface and experience documentation
- **design-system-prompts/** - Design system implementation prompts
- **p0-prompts/** - Phase 0 implementation prompts
- **p1-prompts/** - Phase 1 implementation prompts
- **p1.5-prompts/** - Phase 1.5 implementation prompts
- **phase0-security-prompts/** - Security-focused prompts for Phase 0
- **system-iplementation-assessment/** - System implementation assessments
- **type-check/** - TypeScript type checking documentation
- **uncliassified/** - Documents pending classification

## 🚀 Quick Links

### For New Developers

1. Start with `05-architecture/architecture-overview.md`
2. Review `02-phase-management/P0-IMPLEMENTATION-GUIDE.md`
3. Check `04-guides/QUICK-START-AGENT-SWARM.md`

### For Security Review

- See everything in `01-security/`
- Start with `01-security/SECURITY-AUDIT-FINAL.md`

### For Integration Work

- Check `07-integrations/` for all integration documentation
- Stripe: `stripe-integration-analysis.md`
- Localization: `next-intl-integration.md`

## 📋 Project Phases

- **Phase 0**: Security hardening and bias detection (Completed)
- **Phase 1**: Payment integration with Stripe
- **Phase 1.5**: Subscription management
- **Future Phases**: See `05-architecture/ROADMAP.md`

## 🛠️ Maintenance

To reorganize documentation, run:

```bash
python3 organize_docs.py
```

---

_Documentation organized on: 2025-10-13_
