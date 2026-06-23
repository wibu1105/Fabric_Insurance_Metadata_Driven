import { describe, expect, it } from 'vitest';
import packageJson from '../../package.json';

describe('server runtime scripts', () => {
  it('loads .env for both dev server and start commands', () => {
    expect(packageJson.scripts['dev:server']).toContain('--env-file=.env');
    expect(packageJson.scripts.start).toContain('--env-file=.env');
  });
});
