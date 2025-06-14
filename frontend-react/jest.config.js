export default {
  preset: 'ts-jest/presets/default-esm', // This preset is for projects with "type": "module" in package.json
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'], // Or .js if you prefer
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy', // Mock CSS imports
  },
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.app.json',
        // isolatedModules: true, // This is now handled by tsconfig.app.json
        // useESM: true, // The default-esm preset should handle this
      },
    ],
  },
  extensionsToTreatAsEsm: ['.ts', '.tsx'], // Tell Jest to treat these as ES modules
};