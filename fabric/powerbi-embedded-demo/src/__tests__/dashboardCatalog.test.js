import { describe, expect, it } from 'vitest';
import { dashboards } from '../data/demoConfig.js';

describe('demo configuration', () => {
  it('contains exactly the two requested dashboard entries prepared for embedding', () => {
    expect(dashboards).toHaveLength(2);
    expect(dashboards.map((dashboard) => dashboard.id)).toEqual(['sales-quotation', 'policy-payment-operation']);
    expect(dashboards.map((dashboard) => dashboard.title)).toEqual([
      'Sales & Quotation Dashboard',
      'Policy & Payment Operation Dashboard'
    ]);
    expect(dashboards.map((dashboard) => dashboard.shortTitle)).toEqual([
      'Sales & Quotation',
      'Policy & Payment Operation'
    ]);

    dashboards.forEach((dashboard) => {
      expect(dashboard.embedKey).toMatch(/^[A-Z0-9_]+$/);
      expect(dashboard.summary).toBeTruthy();
      expect(dashboard.metrics.length).toBeGreaterThan(0);
    });
  });

  it('maps dashboards to the correct semantic models', () => {
    const salesQuotation = dashboards.find((dashboard) => dashboard.id === 'sales-quotation');
    const policyPayment = dashboards.find((dashboard) => dashboard.id === 'policy-payment-operation');

    expect(salesQuotation.semanticModels).toEqual(['dashboard_semantic_model']);
    expect(salesQuotation.semanticModelEnvVars).toEqual(['SALES_QUOTATION_DASHBOARD_SEMANTIC_MODEL_ID']);
    expect(policyPayment.semanticModels).toEqual(['OperationalDashboard']);
    expect(policyPayment.semanticModelEnvVars).toEqual([
      'POLICY_PAYMENT_OPERATION_DASHBOARD_SEMANTIC_MODEL_ID',
      'POLICY_PAYMENT_OPERATION_OPERATIONALDASHBOARD_SEMANTIC_MODEL_ID'
    ]);
  });
});
