import { describe, expect, it, vi } from 'vitest';
import { buildLogEntry, maskSensitiveValue, writeApiLog } from '../logger.js';

describe('API debug logger', () => {
  it('masks sensitive query and payload values before writing logs', () => {
    const entry = buildLogEntry({
      event: 'api.request.completed',
      method: 'GET',
      path: '/api/powerbi/embed-config',
      statusCode: 200,
      durationMs: 12,
      query: {
        dashboardId: 'policy-payment-operation',
        userMail: 'AG001@mail.com',
        clientSecret: 'super-secret',
        embedToken: 'token-value'
      }
    });

    expect(entry.query.dashboardId).toBe('policy-payment-operation');
    expect(entry.query.userMail).toBe('AG001@mail.com');
    expect(entry.query.clientSecret).toBe('[redacted]');
    expect(entry.query.embedToken).toBe('[redacted]');
  });

  it('uses structured JSON logs with timestamp and request id', () => {
    const logger = vi.fn();
    writeApiLog({
      logger,
      level: 'info',
      entry: buildLogEntry({
        event: 'powerbi.api.call.completed',
        requestId: 'req-123',
        method: 'POST',
        path: 'https://api.powerbi.com/v1.0/myorg/GenerateToken',
        statusCode: 200,
        durationMs: 34
      })
    });

    expect(logger).toHaveBeenCalledTimes(1);
    const payload = JSON.parse(logger.mock.calls[0][0]);
    expect(payload.event).toBe('powerbi.api.call.completed');
    expect(payload.requestId).toBe('req-123');
    expect(payload.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    expect(payload.durationMs).toBe(34);
  });

  it('masks standalone sensitive values', () => {
    expect(maskSensitiveValue('CLIENT_SECRET', 'abc')).toBe('[redacted]');
    expect(maskSensitiveValue('Authorization', 'Bearer token')).toBe('[redacted]');
    expect(maskSensitiveValue('dashboardId', 'sales-quotation')).toBe('sales-quotation');
  });
});
