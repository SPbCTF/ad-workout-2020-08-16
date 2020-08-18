module.exports = {
  env: { node: true },
  globals: {
    BigInt: true,
  },
  extends: ['eslint:recommended', 'plugin:prettier/recommended'],
  parserOptions: {
    ecmaVersion: 2020,
  },
  plugins: ['prettier'],
  rules: {},
  overrides: [
    {
      files: ['**/*.ts', '**/*.tsx'],
      env: {
        node: true,
      },
      parser: '@typescript-eslint/parser',
      extends: [
        'eslint:recommended',
        'plugin:prettier/recommended',
        'plugin:@typescript-eslint/recommended',
        'prettier/@typescript-eslint',
      ],
      plugins: ['@typescript-eslint', 'prettier'],
    },
  ],
};
