module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/test'],
  testMatch: ['**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coveragePathIgnorePatterns: ['/node_modules/'],
};
