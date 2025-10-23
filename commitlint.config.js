module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',      // New feature
        'fix',       // Bug fix
        'docs',      // Documentation changes
        'style',     // Code style changes (formatting, semicolons, etc)
        'refactor',  // Code refactoring
        'perf',      // Performance improvements
        'test',      // Adding or updating tests
        'build',     // Build system or external dependencies
        'ci',        // CI configuration files and scripts
        'chore',     // Other changes that don't modify src or test files
        'revert',    // Revert a previous commit
      ],
    ],
    'scope-enum': [
      2,
      'always',
      [
        'asr',       // ASR service
        'nlp',       // NLP service
        'backend',   // Backend API
        'frontend',  // Frontend application
        'worker',    // Celery worker
        'infra',     // Infrastructure and DevOps
        'docs',      // Documentation
        'deps',      // Dependencies
        'release',   // Release related
        'config',    // Configuration files
      ],
    ],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [
      2,
      'never',
      ['sentence-case', 'start-case', 'pascal-case', 'upper-case'],
    ],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    'body-leading-blank': [1, 'always'],
    'body-max-line-length': [2, 'always', 100],
    'footer-leading-blank': [1, 'always'],
    'footer-max-line-length': [2, 'always', 100],
    'header-max-length': [2, 'always', 100],
  },
};

