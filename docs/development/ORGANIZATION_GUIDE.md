# Documentation Organization Scripts

This folder contains scripts to organize the CV-Match development documentation.

## 📋 Available Scripts

### 1. `preview_organization.py` - Preview Changes

**Purpose**: Shows what will happen without making any changes

**Usage**:

```bash
python3 preview_organization.py
```

**What it does**:

- Shows the new folder structure
- Lists all files that will be moved
- Verifies all files exist
- Provides statistics
- NO files are moved

### 2. `organize_docs.py` - Execute Organization

**Purpose**: Actually organizes the documentation files

**Usage**:

```bash
python3 organize_docs.py
```

**What it does**:

1. Creates backup marker
2. Creates new folder structure
3. Moves files to appropriate folders
4. Creates README files in each folder
5. Updates main README.md
6. Shows summary of changes

**Safety Features**:

- Asks for confirmation before proceeding
- Creates backup marker
- Provides detailed feedback during execution
- Shows summary of what was done

## 📁 New Folder Structure

After running `organize_docs.py`, your documentation will be organized as:

```
docs/development/
├── 01-security/              # Security audits and reports
├── 02-phase-management/      # P0, P1, P1.5 documentation
├── 03-reports-audits/        # Progress reports and audits
├── 04-guides/                # Implementation guides
├── 05-architecture/          # System architecture docs
├── 06-dependencies/          # Dependency management
├── 07-integrations/          # Third-party integrations
├── 08-assets/                # Static assets (CSS, images)
├── UI-UX/                    # (kept as-is)
├── design-system-prompts/    # (kept as-is)
├── p0-prompts/               # (kept as-is)
├── p1-prompts/               # (kept as-is)
├── p1.5-prompts/             # (kept as-is)
├── phase0-security-prompts/  # (kept as-is)
├── system-iplementation-assessment/ # (kept as-is)
├── type-check/               # (kept as-is)
├── uncliassified/            # (kept as-is)
└── README.md                 # Updated main README
```

## 🚀 Quick Start

1. **First, preview the changes**:

   ```bash
   python3 preview_organization.py
   ```

2. **If everything looks good, organize**:

   ```bash
   python3 organize_docs.py
   ```

3. **Review the results**:
   - Check each new folder
   - Read the README.md in each folder
   - Verify files are in the right place

## 🔄 What Gets Moved

### Security Docs (01-security/)

- All security audit reports
- Security implementation docs
- Critical security fixes

### Phase Management (02-phase-management/)

- P0, P1, P1.5 reports
- Phase completion audits
- Agent swarm strategies
- Bias detection reports

### Reports & Audits (03-reports-audits/)

- Code maturity audits
- Progress reports
- Verification summaries
- Session summaries

### Guides (04-guides/)

- Quick-start guides
- Implementation guides
- Setup guides

### Architecture (05-architecture/)

- System architecture overview
- Business model analysis
- Roadmap

### Dependencies (06-dependencies/)

- Dependency pinning reports
- Dependency maintenance guides

### Integrations (07-integrations/)

- Stripe integration docs
- Next-intl integration
- Resume matcher integration
- Pricing configuration

### Assets (08-assets/)

- CSS files
- Images (if any)

## 📝 What Stays in Place

The following directories are **NOT** modified and remain in their current location:

- `UI-UX/`
- `design-system-prompts/`
- `p0-prompts/`
- `p1-prompts/`
- `p1.5-prompts/`
- `phase0-security-prompts/`
- `system-iplementation-assessment/`
- `type-check/`
- `uncliassified/`

The main `README.md` stays in the root but gets updated with the new structure.

## ⚠️ Important Notes

1. **Backup**: While the script creates a backup marker, you might want to create your own backup before running
2. **Git**: If you're using git, consider committing current changes before organizing
3. **One-way**: The script doesn't have an "undo" feature, so preview carefully
4. **Safe to re-run**: If you need to re-organize, you can run the script again

## 🐛 Troubleshooting

**Problem**: Files not found during preview
**Solution**: Files may have been moved or deleted. Check the preview output.

**Problem**: Permission denied
**Solution**: Make sure scripts are executable:

```bash
chmod +x preview_organization.py organize_docs.py
```

**Problem**: Want to undo changes
**Solution**: If you used git, you can revert. Otherwise, manually move files back.

## 📞 Need Help?

If you encounter issues:

1. Run the preview script first
2. Check the output for errors
3. Review this guide
4. Check individual folder READMEs after organization

---

_Scripts created: 2025-10-13_
