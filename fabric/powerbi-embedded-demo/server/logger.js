const SENSITIVE_KEY_PATTERN = /(secret|token|authorization|password|credential|assertion|key)$/i;

export function maskSensitiveValue(key, value) {
  if (SENSITIVE_KEY_PATTERN.test(key)) {
    return '[redacted]';
  }
  return value;
}

export function sanitizeLogObject(value) {
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeLogObject(item));
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, maskSensitiveValue(key, sanitizeLogObject(item))])
    );
  }

  return value;
}

export function buildLogEntry(entry) {
  return sanitizeLogObject({
    timestamp: new Date().toISOString(),
    ...entry
  });
}

export function writeApiLog({ logger = console.log, level = 'info', entry }) {
  logger(JSON.stringify({ level, ...entry }));
}

export function logInfo(entry) {
  writeApiLog({ level: 'info', entry: buildLogEntry(entry) });
}

export function logError(entry) {
  writeApiLog({ logger: console.error, level: 'error', entry: buildLogEntry(entry) });
}

export function createRequestLogger() {
  return (request, response, next) => {
    const start = performance.now();
    const requestId = request.headers['x-request-id'] ?? crypto.randomUUID();
    request.requestId = requestId;
    response.setHeader('x-request-id', requestId);

    response.on('finish', () => {
      logInfo({
        event: 'api.request.completed',
        requestId,
        method: request.method,
        path: request.originalUrl ?? request.url,
        route: request.path,
        statusCode: response.statusCode,
        durationMs: Math.round(performance.now() - start),
        query: request.query
      });
    });

    next();
  };
}
