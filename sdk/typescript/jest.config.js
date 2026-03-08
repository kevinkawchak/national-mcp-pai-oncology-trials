/**
 * Jest configuration for the @trialmcp/sdk package.
 *
 * Uses ts-jest for TypeScript support with strict mode matching
 * the tsconfig.json settings. Tests are co-located in the tests/
 * directory.
 */

/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: [
    '**/*.test.ts',
    '**/*.spec.ts',
  ],
  transform: {
    '^.+\\.ts$': [
      'ts-jest',
      {
        tsconfig: {
          target: 'ES2020',
          module: 'commonjs',
          strict: true,
          esModuleInterop: true,
          skipLibCheck: true,
          forceConsistentCasingInFileNames: true,
          resolveJsonModule: true,
          declaration: false,
          sourceMap: true,
          rootDir: '..',
        },
      },
    ],
  },
  moduleNameMapper: {
    '^@trialmcp/sdk$': '<rootDir>/src/index.ts',
    '^@trialmcp/sdk/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/index.ts',
    '!src/middleware/index.ts',
    '!src/models/index.ts',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'clover'],
  coverageThresholds: {
    global: {
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  verbose: true,
  testTimeout: 10000,
};
