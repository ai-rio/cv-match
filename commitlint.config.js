module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation changes
        'style',    // Code style changes (formatting, etc)
        'refactor', // Code refactoring
        'perf',     // Performance improvements
        'test',     // Test additions/modifications
        'chore',    // Maintenance tasks
        'build',    // Build system changes
        'ci',       // CI configuration changes
        'revert',   // Revert previous commit
        'bump',     // Version bump
        'lint',     // Linting fixes
        'security', // Security fixes
        'deps',     // Dependency updates
        'i18n',     // Internationalization changes
        'wip'       // Work in progress
      ]
    ],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'type-empty': [2, 'never'],
    'scope-case': [2, 'always', 'lower-case'],
    'scope-empty': [0], // Optional scope
    'body-leading-blank': [1, 'always'],
    'footer-leading-blank': [1, 'always']
  },
  // Custom parser preset for Brazilian market context
  parserPreset: {
    parserOpts: {
      issuePrefixes: ['BRL-', 'CV-']
    }
  }
};