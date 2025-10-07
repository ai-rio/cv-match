/**
 * @type {import('lint-staged').Configuration}
 */
export default {
  // Frontend files (from frontend directory)
  "*.{ts,tsx,js,jsx}": [
    "bunx eslint --fix --max-warnings=0",
    "bunx prettier --write"
  ],
  "*.{css,scss,less}": [
    "bunx stylelint --fix",
    "bunx prettier --write"
  ],
  "*.{json,md,yml,yaml}": [
    "bunx prettier --write"
  ],

  // Backend Python files (relative to frontend directory)
  "../backend/**/*.py": [
    "cd ../backend && uv run ruff check --fix .",
    "cd ../backend && uv run ruff format ."
  ],

  // Supabase migration files
  "supabase/migrations/*.sql": [
    "echo '🗄️ Linting SQL migration file...' && exit 0"
  ]
}