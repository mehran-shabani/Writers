module.exports = {
  branches: [
    'main',
    {
      name: 'develop',
      prerelease: true,
    },
    {
      name: 'beta',
      prerelease: true,
    },
  ],
  plugins: [
    [
      '@semantic-release/commit-analyzer',
      {
        preset: 'conventionalcommits',
        releaseRules: [
          { type: 'feat', release: 'minor' },
          { type: 'fix', release: 'patch' },
          { type: 'perf', release: 'patch' },
          { type: 'revert', release: 'patch' },
          { type: 'docs', release: false },
          { type: 'style', release: false },
          { type: 'chore', release: false },
          { type: 'refactor', release: 'patch' },
          { type: 'test', release: false },
          { type: 'build', release: false },
          { type: 'ci', release: false },
          { scope: 'no-release', release: false },
        ],
        parserOpts: {
          noteKeywords: ['BREAKING CHANGE', 'BREAKING CHANGES', 'BREAKING'],
        },
      },
    ],
    [
      '@semantic-release/release-notes-generator',
      {
        preset: 'conventionalcommits',
        presetConfig: {
          types: [
            { type: 'feat', section: '🚀 Features', hidden: false },
            { type: 'fix', section: '🐛 Bug Fixes', hidden: false },
            { type: 'perf', section: '⚡ Performance Improvements', hidden: false },
            { type: 'revert', section: '⏪ Reverts', hidden: false },
            { type: 'docs', section: '📝 Documentation', hidden: false },
            { type: 'style', section: '💄 Styles', hidden: true },
            { type: 'chore', section: '🔧 Miscellaneous Chores', hidden: true },
            { type: 'refactor', section: '♻️ Code Refactoring', hidden: false },
            { type: 'test', section: '✅ Tests', hidden: true },
            { type: 'build', section: '📦 Build System', hidden: true },
            { type: 'ci', section: '👷 CI/CD', hidden: true },
          ],
        },
        writerOpts: {
          commitsSort: ['scope', 'subject'],
        },
      },
    ],
    [
      '@semantic-release/changelog',
      {
        changelogFile: 'CHANGELOG.md',
        changelogTitle: '# Changelog\n\nAll notable changes to this project will be documented in this file.',
      },
    ],
    [
      '@semantic-release/npm',
      {
        npmPublish: false,
      },
    ],
    [
      '@semantic-release/git',
      {
        assets: ['CHANGELOG.md', 'package.json', 'package-lock.json'],
        message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
      },
    ],
    [
      '@semantic-release/github',
      {
        successComment: false,
        failComment: false,
        failTitle: false,
        labels: ['released'],
        releasedLabels: ['released<%= nextRelease.channel ? `-${nextRelease.channel}` : "" %>'],
      },
    ],
  ],
};

