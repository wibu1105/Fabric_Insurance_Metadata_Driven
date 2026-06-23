import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

beforeEach(() => {
  window.localStorage.clear();
  globalThis.fetch = vi.fn(async (url) => {
    if (String(url).startsWith('/api/auth/microsoft/status')) {
      return {
        ok: true,
        json: async () => ({ microsoftAuthenticated: true })
      };
    }

    if (String(url).startsWith('/api/auth/me')) {
      return {
        ok: false,
        status: 401,
        text: async () => 'Mock user authentication required.'
      };
    }

    if (String(url).startsWith('/api/auth/users')) {
      return {
        ok: true,
        json: async () => ({
          users: [
            {
              id: 'EXECUTIVE@mail.com',
              userMail: 'EXECUTIVE@mail.com',
              username: 'EXECUTIVE@mail.com',
              effectiveUsername: 'EXECUTIVE',
              role: 'Admin',
              rlsLevel: 1,
              accessValue: null,
              powerbiUsername: 'EXECUTIVE',
              powerbiRoles: ['rls_level']
            },
            {
              id: 'AG001@mail.com',
              userMail: 'AG001@mail.com',
              username: 'AG001@mail.com',
              effectiveUsername: 'AG001',
              role: 'Agent',
              rlsLevel: 2,
              accessValue: 'AG001',
              powerbiUsername: 'AG001',
              powerbiRoles: ['rls_level']
            }
          ]
        })
      };
    }

    if (String(url).startsWith('/api/auth/login')) {
      return {
        ok: true,
        json: async () => ({
          token: 'test-session-token',
          user: {
            id: 'EXECUTIVE@mail.com',
            userMail: 'EXECUTIVE@mail.com',
            username: 'EXECUTIVE@mail.com',
            effectiveUsername: 'EXECUTIVE',
            role: 'Admin',
            rlsLevel: 1,
            accessValue: null,
            powerbiUsername: 'EXECUTIVE',
            powerbiRoles: ['rls_level']
          }
        })
      };
    }

    if (String(url).startsWith('/api/auth/change-password')) {
      return {
        ok: true,
        json: async () => ({
          token: 'test-session-token-2',
          user: {
            id: 'EXECUTIVE@mail.com',
            userMail: 'EXECUTIVE@mail.com',
            username: 'EXECUTIVE@mail.com',
            effectiveUsername: 'EXECUTIVE',
            role: 'Admin',
            rlsLevel: 1,
            accessValue: null,
            powerbiUsername: 'EXECUTIVE',
            powerbiRoles: ['rls_level']
          }
        })
      };
    }

    return {
      ok: true,
      json: async () => ({
        mode: 'demo',
        embedToken: null,
        message: 'Demo mode is active.'
      })
    };
  });
});
