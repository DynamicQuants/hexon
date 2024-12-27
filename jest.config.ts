import { jestNestjsLib } from '@dynamic-quants/config-tools/jest';
import type { Config } from 'jest';

export default {
  ...jestNestjsLib,
  displayName: '@dynamic-quants/hexon',
  transformIgnorePatterns: ['node_modules/(?!(nanoid))/'],
} as Config;
