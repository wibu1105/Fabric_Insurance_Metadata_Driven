import { describe, expect, it } from 'vitest';

import {
  hasValidMicrosoftToken,
  readMicrosoftAccessToken,
  storeMicrosoftToken
} from '../microsoftInteractiveAuth.js';

describe('Microsoft interactive admin session auth', () => {
  it('recognizes missing and expired Microsoft master tokens', () => {
    expect(hasValidMicrosoftToken({})).toBe(false);
    expect(
      hasValidMicrosoftToken({
        microsoftAuth: {
          accessToken: 'expired-token',
          expiresOn: new Date('2026-06-16T00:00:00.000Z').toISOString()
        }
      }, new Date('2026-06-16T00:10:00.000Z'))
    ).toBe(false);
  });

  it('stores and reads the Microsoft master token from server-side session only', () => {
    const session = {};
    storeMicrosoftToken(session, {
      accessToken: 'master-powerbi-token',
      expiresOn: new Date('2026-06-16T02:00:00.000Z'),
      account: { username: 'presenter@nashtech.com' }
    });

    expect(hasValidMicrosoftToken(session, new Date('2026-06-16T01:00:00.000Z'))).toBe(true);
    expect(readMicrosoftAccessToken({ session }, new Date('2026-06-16T01:00:00.000Z'))).toBe('master-powerbi-token');
    expect(session.microsoftAuth.accountUsername).toBe('presenter@nashtech.com');
  });
});
