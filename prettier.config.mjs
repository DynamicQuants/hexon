import prettier from '@dynamic-quants/config-tools/prettier';

const config = {
  ...prettier,
  importOrder: ['@/', ...prettier.importOrder],
};

export default config;
