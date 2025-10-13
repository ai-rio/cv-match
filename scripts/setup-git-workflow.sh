#!/bin/bash

echo "🚀 Setting up Enterprise Git Workflow for CV-Match..."

# Fix permissions first
echo "🔧 Fixing directory permissions..."
sudo chown -R $USER:$USER frontend 2>/dev/null || true
sudo chmod -R 755 frontend 2>/dev/null || true
sudo chown -R $USER:$USER .husky 2>/dev/null || true

# Install frontend dependencies with BUN ONLY
echo "📦 Installing frontend dependencies with bun..."
cd frontend
if command -v bun &> /dev/null; then
    bun install
else
    echo "❌ BUN IS REQUIRED! Please install bun first: https://bun.sh/"
    echo "curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Install backend Python dependencies with UV ONLY
echo "🐍 Installing backend dependencies with uv..."
cd ../backend
if command -v uv &> /dev/null; then
    uv sync
else
    echo "❌ UV IS REQUIRED! Please install uv first: https://docs.astral.sh/uv/"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Go back to root
cd ..

# Install global dependencies (only husky)
echo "🌐 Installing global dependencies..."
# We'll install husky globally with bun in the frontend dir
cd frontend && bun add husky --dev && cd ..

# Initialize Git hooks
echo "🎣 Initializing Git hooks..."
cd frontend && bunx prepare && cd ..

# Make hooks executable
echo "🔐 Making hooks executable..."
chmod +x .husky/*

echo "✅ Enterprise Git Workflow setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. All dependencies are installed!"
echo "2. Read the workflow documentation: docs/GIT-WORKFLOW.md"
echo "3. Test the workflow by making a commit"
echo ""
echo "🎯 Your Git workflow is now ready for enterprise development!"
echo "💡 REMEMBER: Use ONLY bun for frontend and uv for backend!"
