export function buildGenerateTokenRequest({ reportId, semanticModelIds, account }) {
  return {
    datasets: semanticModelIds.map((semanticModelId) => ({
      id: semanticModelId,
      xmlaPermissions: 'ReadOnly'
    })),
    reports: [{ id: reportId, allowEdit: false }],
    identities: [
      {
        username: account.powerbiUsername,
        roles: account.powerbiRoles,
        datasets: semanticModelIds,
        customData: JSON.stringify({
          rls_level: account.rlsLevel,
          access_value: account.accessValue ?? null
        })
      }
    ]
  };
}
