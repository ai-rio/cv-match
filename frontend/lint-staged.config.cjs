module.exports = {
  "*.{ts,tsx,js,jsx}": [
    "eslint --fix --max-warnings=10 --config eslint.config.mjs",
    "prettier --write"
  ],
  "*.{css,scss,less}": [
    "prettier --write"
  ],
  "*.{json,md,yml,yaml}": [
    "prettier --write"
  ]
}
