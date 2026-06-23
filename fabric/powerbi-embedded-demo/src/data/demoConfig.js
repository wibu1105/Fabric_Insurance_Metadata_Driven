export const dashboards = [
  {
    id: 'sales-quotation',
    embedKey: 'SALES_QUOTATION',
    title: 'Sales & Quotation Dashboard',
    shortTitle: 'Sales & Quotation',
    sourceArtifact: 'quotation_sale.Report',
    semanticModels: ['dashboard_semantic_model'],
    semanticModelEnvVars: ['SALES_QUOTATION_DASHBOARD_SEMANTIC_MODEL_ID'],
    audience: 'Business users, sales leads, branch managers, executives',
    summary:
      'Business dashboard for the CarPro insurance domain. It demonstrates sales performance, quotation status, premium analytics, provider performance, and branch or agent activity with RLS-aware website access.',
    metrics: ['Quotation status', 'Premium amount', 'Policy conversion', 'Provider performance', 'Agent and branch activity']
  },
  {
    id: 'policy-payment-operation',
    embedKey: 'POLICY_PAYMENT_OPERATION',
    title: 'Policy & Payment Operation Dashboard',
    shortTitle: 'Policy & Payment Operation',
    sourceArtifact: 'Policy and payment operation Power BI report',
    semanticModels: ['OperationalDashboard'],
    semanticModelEnvVars: [
      'POLICY_PAYMENT_OPERATION_DASHBOARD_SEMANTIC_MODEL_ID',
      'POLICY_PAYMENT_OPERATION_OPERATIONALDASHBOARD_SEMANTIC_MODEL_ID'
    ],
    audience: 'Operations team, policy administrators, payment reviewers, branch managers',
    summary:
      'Operational dashboard for policy issuance, policy lifecycle tracking, payment collection, cancellation visibility, and outstanding payment review across the CarPro process.',
    metrics: ['Issued policies', 'Active policies', 'Payment collection', 'Outstanding payments', 'Cancellation trend', 'Operation status']
  }
];

export const defaultDashboardId = dashboards[0].id;
