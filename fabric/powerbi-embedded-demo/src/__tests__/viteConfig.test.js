import { describe, expect, it } from 'vitest';

import viteConfig from '../../vite.config.js';

describe('vite development server configuration', () => {
  it('proxies /api requests to the Node backend on port 8080', () => {
    expect(viteConfig.server?.proxy?.['/api']).toBe('http://localhost:8080');
  });
});
