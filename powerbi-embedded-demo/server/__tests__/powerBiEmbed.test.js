import { describe, expect, it } from 'vitest';

import { buildGenerateTokenRequest } from '../powerBiEmbed.js';

describe('Power BI embed token request payload', () => {
  it('injects the mock warehouse user into effective identities for RLS', () => {
    const payload = buildGenerateTokenRequest({
      workspaceId: 'workspace-guid',
      reportId: 'report-guid',
      semanticModelIds: ['semantic-model-guid'],
      account: {
        userMail: 'AG001@mail.com',
        effectiveUsername: 'AG001',
        powerbiUsername: 'AG001',
        powerbiRoles: ['rls_level'],
        rlsLevel: 2,
        accessValue: 'AG001'
      }
    });

    expect(payload).toEqual({
      datasets: [{ id: 'semantic-model-guid', xmlaPermissions: 'ReadOnly' }],
      reports: [{ id: 'report-guid', allowEdit: false }],
      identities: [
        {
          username: 'AG001',
          roles: ['rls_level'],
          datasets: ['semantic-model-guid'],
          customData: JSON.stringify({
            rls_level: 2,
            access_value: 'AG001'
          })
        }
      ]
    });
  });
});
