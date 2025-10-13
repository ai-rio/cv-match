# UV Troubleshooting Guide - CV-Match Brazilian SaaS

## Overview

This guide covers common UV issues and solutions encountered during the CV-Match project development, particularly when working with Sentry integration and Python package management.

## 🚀 Quick UV Commands

### Basic Operations

```bash
# Create virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.12

# Create with custom name
uv venv my-project-env

# Activate environment
source .venv/bin/activate

# Install packages
uv pip install package-name

# Install with version constraints
uv pip install 'package>=1.0,<2.0'

# Install from requirements.txt
uv pip install -r requirements.txt

# Install packages with extras (proper syntax)
uv pip install 'sentry-sdk[fastapi]==1.40.6'

# Check installed packages
uv pip list

# Check environment consistency
uv pip check

# Create requirements file
uv pip freeze > requirements.txt
```

## 🔧 Common Issues and Solutions

### 1. Broken Python Symlinks in Virtual Environment

**Problem**:

```
error: Failed to inspect Python interpreter from virtual environment at `.venv/bin/python3`
Caused by: Broken symlink at `.venv/bin/python3`, was the underlying Python interpreter removed?
```

**Solution 1: Use existing working environment**

```bash
# Check if .venv-fixed exists and works
source .venv-fixed/bin/activate
python --version

# If working, use this environment for development
```

**Solution 2: Create new virtual environment**

```bash
# Remove broken environment (if permissions allow)
rm -rf .venv

# Create new environment
uv venv .venv-new

# Or use specific Python version
uv venv --python 3.12 .venv-new

# Activate new environment
source .venv-new/bin/activate
```

**Solution 3: Fix broken symlinks manually**

```bash
# Find correct Python path
which python3
# Example output: /home/linuxbrew/.linuxbrew/bin/python3

# Remove broken symlinks (if permissions allow)
rm -f .venv/bin/python .venv/bin/python3 .venv/bin/python3.12

# Create correct symlinks
ln -s /home/linuxbrew/.linuxbrew/bin/python3 .venv/bin/python
ln -s python .venv/bin/python3
ln -s python .venv/bin/python3.12
```

### 2. Permission Issues

**Problem**:

```
error: Failed to create file `/path/to/.venv/bin/activate`: Permission denied (os error 13)
```

**Solution**:

```bash
# Check current user and directory ownership
whoami
ls -la

# If files are owned by root, change ownership
sudo chown -R carlos:carlos .venv*

# Or create environment in user-owned directory
mkdir -p ~/.venvs
uv venv ~/.venvs/cv-match
source ~/.venvs/cv-match/bin/activate
```

### 3. Package Installation with Extras

**Problem**: Shell interpretation issues with brackets

```bash
# This will fail due to shell interpretation
uv pip install sentry-sdk[fastapi]==1.40.6
```

**Solution**: Proper quoting

```bash
# Single quotes (recommended)
uv pip install 'sentry-sdk[fastapi]==1.40.6'

# Double quotes (alternative)
uv pip install "sentry-sdk[fastapi]==1.40.6"

# Escaping brackets (less common)
uv pip install sentry-sdk\[fastapi\]==1.40.6
```

### 4. Multiple Python Environments

**Problem**: Confusion between system Python and virtual environments

**Solution**: Explicit environment specification

```bash
# Use specific virtual environment
VIRTUAL_ENV=/path/to/.venv uv pip install package

# Or activate first, then install
source .venv/bin/activate
uv pip install package

# Check current environment
python -c "import sys; print(sys.prefix)"

# List all available Python versions
uv python list
```

### 5. Build Dependencies Missing

**Problem**:

```
error: Failed to build wheels, which required Python and setuptools packages to be installed
```

**Solution**: Install build dependencies

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install build-essential python3-dev

# On CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# On macOS
xcode-select --install
```

### 6. Package Cache Issues

**Problem**: Stale or corrupted package cache

**Solution**:

```bash
# Clear UV cache
uv cache clean

# Reinstall packages
uv pip install --force-reinstall -r requirements.txt

# Or create fresh environment
rm -rf .venv
uv venv
uv pip install -r requirements.txt
```

## 🛠️ CV-Match Specific Solutions

### Sentry Integration Issues

**Problem**: Sentry installation fails with bracket syntax

```bash
# Incorrect (will fail)
uv pip install sentry-sdk[fastapi]==1.40.6
```

**Solution**: Use proper quoting

```bash
# Correct approach
source .venv-fixed/bin/activate
uv pip install 'sentry-sdk[fastapi]==1.40.6'

# Or install from requirements.txt
echo 'sentry-sdk[fastapi]==1.40.6' >> requirements.txt
uv pip install -r requirements.txt
```

### Multiple Virtual Environments

**CV-Match Project Structure**:

```
backend/
├── .venv           # Original broken environment
├── .venv-fixed     # Working environment (use this)
├── .venv-new       # Alternative working environment
└── test-venv       # Test environment
```

**Recommended Workflow**:

```bash
# Use the working fixed environment
cd backend
source .venv-fixed/bin/activate

# Install new packages
uv pip install 'new-package'

# Update requirements.txt
uv pip freeze > requirements.txt

# Test new environment before deployment
uv venv test-deployment
source test-deployment/bin/activate
uv pip install -r requirements.txt
python -m pytest
```

## 📋 Environment Management Best Practices

### 1. Use Consistent Environment Names

```bash
# Good naming convention
uv venv cv-match-backend
uv venv cv-match-frontend
uv venv cv-match-testing

# Activate
source cv-match-backend/bin/activate
```

### 2. Keep requirements.txt Updated

```bash
# After installing new packages
uv pip freeze > requirements.txt

# Commit to version control
git add requirements.txt
git commit -m "chore: update dependencies"
```

### 3. Use Environment-Specific Configurations

```bash
# Development environment
uv venv dev-env
source dev-env/bin/activate
uv pip install -r requirements-dev.txt

# Production environment
uv venv prod-env
source prod-env/bin/activate
uv pip install -r requirements.txt
```

### 4. Test Environment Reproducibility

```bash
# Create fresh environment from requirements
uv venv test-repro
source test-repro/bin/activate
uv pip install -r requirements.txt

# Run tests to verify
python -m pytest
python -c "from app.core.sentry import init_sentry; print('✅ Imports work')"
```

## 🔄 UV vs pip Comparison

### UV Advantages

- **Speed**: 10-100x faster than pip
- **Rust-based**: More reliable and efficient
- **Built-in caching**: Better dependency resolution
- **Modern dependency management**: Supports pyproject.toml

### When to Use UV

- ✅ New Python projects
- ✅ Fast dependency installation
- ✅ Modern Python packaging (pyproject.toml)
- ✅ CI/CD pipelines
- ✅ Development environments

### When to Use pip

- ✅ Legacy projects
- ✅ Specific pip-only features
- ✅ Corporate environments with pip requirements
- ✅ When UV has compatibility issues

## 🚨 Emergency Procedures

### If UV Completely Fails

**Fallback to pip**:

```bash
# Use system Python venv
python3 -m venv .emergency-env
source .emergency-env/bin/activate

# Install packages with pip
pip install -r requirements.txt
pip install 'sentry-sdk[fastapi]==1.40.6'
```

### If All Virtual Environments Fail

**System-wide installation (not recommended for development)**:

```bash
# Install to system Python (requires admin rights)
sudo pip install 'sentry-sdk[fastapi]==1.40.6'

# Or use --user flag
pip install --user 'sentry-sdk[fastapi]==1.40.6'
```

## 📚 Additional Resources

### Official Documentation

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)

### CV-Match Project Specific

- Sentry Integration Guide: `docs/SENTRY-INTEGRATION-SUMMARY.md`
- Development Workflow: `docs/development/README.md`
- Project Configuration: `pyproject.toml`

### Common Commands Reference

```bash
# UV version
uv --version

# Python version management
uv python install 3.12
uv python list
uv python pin 3.12

# Package management
uv pip list
uv pip show package-name
uv pip uninstall package-name
uv pip check

# Environment management
uv venv --help
uv pip --help
```

---

## 🎯 Quick Fix Checklist

When facing UV issues, follow this checklist:

1. **Check current environment**: `which python3` and `python3 --version`
2. **Try existing working venv**: `source .venv-fixed/bin/activate`
3. **Create new environment**: `uv venv test-env`
4. **Use proper package syntax**: `uv pip install 'package[extras]==version'`
5. **Check permissions**: `ls -la .venv*`
6. **Clear cache if needed**: `uv cache clean`
7. **Fall back to pip**: `python3 -m venv .pip-env && source .pip-env/bin/activate`

---

**Last Updated**: 2025-10-13
**Project**: CV-Match Brazilian SaaS
**UV Version**: Latest (check with `uv --version`)
