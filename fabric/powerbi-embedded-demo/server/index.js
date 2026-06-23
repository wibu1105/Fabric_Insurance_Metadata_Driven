import 'dotenv/config';
import express from 'express';
import session from 'express-session';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { dashboards } from '../src/data/demoConfig.js';
import { createRequestLogger, logError, logInfo } from './logger.js';
import {
  acquireMicrosoftTokenFromCode,
  createMicrosoftLoginUrl,
  microsoftStatus,
  readMicrosoftAccessToken,
  storeMicrosoftToken
} from './microsoftInteractiveAuth.js';
import { buildGenerateTokenRequest } from './powerBiEmbed.js';
import { authenticateAppUser, changeAppUserPassword, listAppUsers } from './warehouseUsers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = process.env.PORT || 8080;
const demoMode = process.env.DEMO_MODE !== 'false';

const dashboardConfig = Object.fromEntries(
  dashboards.map((dashboard) => [
    dashboard.id,
    {
      envPrefix: dashboard.embedKey,
      title: dashboard.title,
      semanticModelEnvVars: dashboard.semanticModelEnvVars
    }
  ])
);

app.set('trust proxy', 1);
app.use(express.json());
app.use(
  session({
    name: 'carpro.sid',
    secret: readServerSessionSecret(),
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.SESSION_COOKIE_SECURE === 'true',
      maxAge: Number(process.env.SESSION_MAX_AGE_MS || 8 * 60 * 60 * 1000)
    }
  })
);
app.use(createRequestLogger());

app.get('/api/health', (_request, response) => {
  response.json({ status: 'ok', service: 'powerbi-embedded-demo' });
});

app.get('/api/auth/microsoft/status', (request, response) => {
  response.json(microsoftStatus(request.session));
});

app.get('/api/auth/microsoft/login', async (request, response) => {
  try {
    const loginUrl = await createMicrosoftLoginUrl(request);
    return response.redirect(loginUrl);
  } catch (error) {
    logError({
      event: 'auth.microsoft.login.failed',
      requestId: request.requestId,
      errorName: error.name,
      errorMessage: error.message
    });
    return response.status(error.statusCode ?? 500).send(error.publicMessage ?? 'Microsoft sign-in failed.');
  }
});

app.get('/api/auth/microsoft/callback', async (request, response) => {
  try {
    const tokenResponse = await acquireMicrosoftTokenFromCode(request);
    storeMicrosoftToken(request.session, tokenResponse);

    logInfo({
      event: 'auth.microsoft.login.succeeded',
      requestId: request.requestId,
      accountUsername: request.session.microsoftAuth?.accountUsername,
      expiresOn: request.session.microsoftAuth?.expiresOn
    });

    return response.redirect(process.env.FRONTEND_APP_URL || '/');
  } catch (error) {
    logError({
      event: 'auth.microsoft.callback.failed',
      requestId: request.requestId,
      errorName: error.name,
      errorMessage: error.message
    });
    return response.status(error.statusCode ?? 500).send(error.publicMessage ?? 'Microsoft sign-in callback failed.');
  }
});

app.get('/api/auth/users', async (request, response) => {
  try {
    const users = await listAppUsers();
    return response.json({ users: users.map(withPowerBiRole) });
  } catch (error) {
    logError({
      event: 'auth.users.failed',
      requestId: request.requestId,
      errorName: error.name,
      errorMessage: error.message
    });

    return response.status(500).send('Unable to read warehouse users.');
  }
});

app.post('/api/auth/login', async (request, response) => {
  try {
    const user = withPowerBiRole(await authenticateAppUser(request.body ?? {}));
    request.session.appUser = user;

    logInfo({
      event: 'auth.login.succeeded',
      requestId: request.requestId,
      userMail: user.userMail,
      effectiveUsername: user.userMail,
      rlsLevel: user.rlsLevel,
      accessValue: user.accessValue
    });

    return response.json({ user });
  } catch (error) {
    logError({
      event: 'auth.login.failed',
      requestId: request.requestId,
      userMail: request.body?.userMail,
      errorName: error.name,
      errorMessage: error.message
    });

    return response.status(error.statusCode ?? 500).send(error.publicMessage ?? 'Login failed.');
  }
});

app.get('/api/auth/me', (request, response) => {
  try {
    const user = readAuthenticatedUser(request);
    return response.json({ user: withPowerBiRole(user) });
  } catch (error) {
    return response.status(error.statusCode ?? 401).send(error.publicMessage ?? 'Authentication required.');
  }
});

app.post('/api/auth/logout', (request, response) => {
  delete request.session.appUser;
  response.status(204).send();
});

app.post('/api/auth/change-password', async (request, response) => {
  try {
    const currentUser = readAuthenticatedUser(request);
    const user = withPowerBiRole(await changeAppUserPassword({
      userMail: currentUser.userMail,
      currentPassword: request.body?.currentPassword,
      newPassword: request.body?.newPassword
    }));
    request.session.appUser = user;

    logInfo({
      event: 'auth.change-password.succeeded',
      requestId: request.requestId,
      userMail: user.userMail
    });

    return response.json({ user });
  } catch (error) {
    logError({
      event: 'auth.change-password.failed',
      requestId: request.requestId,
      errorName: error.name,
      errorMessage: error.message
    });

    return response.status(error.statusCode ?? 500).send(error.publicMessage ?? 'Password change failed.');
  }
});

app.get('/api/powerbi/embed-config', async (request, response) => {
  const { dashboardId } = request.query;
  const dashboard = dashboardConfig[dashboardId];

  if (!dashboard) {
    return response.status(404).send('Unknown dashboard requested.');
  }

  let account;
  try {
    account = withPowerBiRole(readAuthenticatedUser(request));
  } catch (error) {
    return response.status(error.statusCode ?? 401).send(error.publicMessage ?? 'Authentication required.');
  }

  if (demoMode) {
    logInfo({
      event: 'powerbi.embed-config.demo',
      requestId: request.requestId,
      dashboardId,
      userMail: account.userMail,
      effectiveUsername: account.userMail,
      semanticModelEnvVars: dashboard.semanticModelEnvVars
    });

    return response.json({
      mode: 'demo',
      dashboardId,
      reportId: null,
      embedUrl: null,
      embedToken: null,
      message: 'Demo mode is active. Set DEMO_MODE=false and provide Power BI environment variables to enable live embedding.'
    });
  }

  try {
    const masterAccessToken = readMicrosoftAccessToken(request);
    const embedConfig = await buildEmbedConfig(dashboard, account, request.requestId, masterAccessToken);
    return response.json(embedConfig);
  } catch (error) {
    logError({
      event: 'powerbi.embed-config.failed',
      requestId: request.requestId,
      dashboardId,
      userMail: account.userMail,
      effectiveUsername: account.userMail,
      errorName: error.name,
      errorMessage: error.message
    });
    return response.status(error.statusCode ?? 500).send(error.publicMessage ?? 'Failed to generate Power BI embed configuration. Check the server logs with the response x-request-id.');
  }
});

async function buildEmbedConfig(dashboard, account, requestId, accessToken) {
  const workspaceId = readRequiredEnv(`${dashboard.envPrefix}_WORKSPACE_ID`);
  const reportId = readRequiredEnv(`${dashboard.envPrefix}_REPORT_ID`);
  const configuredSemanticModelIds = dashboard.semanticModelEnvVars.map((envVar) => readRequiredEnv(envVar));

  logInfo({
    event: 'powerbi.embed-config.live.start',
    requestId,
    dashboard: dashboard.title,
    reportEnvVar: `${dashboard.envPrefix}_REPORT_ID`,
    semanticModelEnvVars: dashboard.semanticModelEnvVars,
    userMail: account.userMail,
    effectiveUsername: account.userMail,
    rlsLevel: account.rlsLevel,
    accessValue: account.accessValue
  });

  const report = await getReportMetadata({ accessToken, workspaceId, reportId, requestId });
  const semanticModelIds = uniqueValues([
    report.datasetId,
    ...configuredSemanticModelIds
  ]);

  logInfo({
    event: 'powerbi.embed-config.live.datasets',
    requestId,
    reportDatasetId: report.datasetId ?? null,
    configuredSemanticModelIds,
    tokenSemanticModelIds: semanticModelIds
  });

  const embedToken = await generateEmbedToken({ accessToken, workspaceId, reportId, semanticModelIds, account, requestId });

  return {
    mode: 'live',
    dashboardId: dashboard.envPrefix,
    reportId,
    semanticModelIds,
    embedUrl: report.embedUrl,
    embedToken: embedToken.token,
    expiresAt: embedToken.expiration
  };
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))];
}


async function getReportMetadata({ accessToken, workspaceId, reportId, requestId }) {
  const url = `https://api.powerbi.com/v1.0/myorg/groups/${workspaceId}/reports/${reportId}`;
  const start = performance.now();
  logInfo({
    event: 'powerbi.api.call.started',
    requestId,
    method: 'GET',
    path: url,
    workspaceId,
    reportId
  });

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });

  logInfo({
    event: 'powerbi.api.call.completed',
    requestId,
    method: 'GET',
    path: url,
    statusCode: response.status,
    durationMs: Math.round(performance.now() - start)
  });

  if (!response.ok) {
    throw powerBiApiError('Failed to read Power BI report metadata', response.status, await response.text());
  }

  return response.json();
}

async function generateEmbedToken({ accessToken, workspaceId, reportId, semanticModelIds, account, requestId }) {
  const body = buildGenerateTokenRequest({ workspaceId, reportId, semanticModelIds, account });

  const url = 'https://api.powerbi.com/v1.0/myorg/GenerateToken';
  const start = performance.now();
  logInfo({
    event: 'powerbi.api.call.started',
    requestId,
    method: 'POST',
    path: url,
    workspaceId,
    reportId,
    semanticModelCount: semanticModelIds.length,
    userMail: account.userMail,
    effectiveUsername: account.userMail,
    powerbiUsername: account.userMail,
    powerbiRoles: account.powerbiRoles
  });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  logInfo({
    event: 'powerbi.api.call.completed',
    requestId,
    method: 'POST',
    path: url,
    statusCode: response.status,
    durationMs: Math.round(performance.now() - start),
    semanticModelCount: semanticModelIds.length
  });

  if (!response.ok) {
    throw powerBiApiError('Failed to generate Power BI embed token', response.status, await response.text());
  }

  return response.json();
}

function readRequiredEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw configurationError(`Missing required environment variable: ${name}`);
  }
  return value;
}

function readServerSessionSecret() {
  if (process.env.SESSION_SECRET) {
    return process.env.SESSION_SECRET;
  }

  if (process.env.NODE_ENV === 'production') {
    throw configurationError('Missing required environment variable: SESSION_SECRET');
  }

  return 'local-development-session-secret-change-before-deployment';
}

function configurationError(message) {
  const error = new Error(message);
  error.publicMessage = message;
  return error;
}

function powerBiApiError(message, statusCode, responseText) {
  const error = new Error(`${message}: ${statusCode} ${responseText}`);
  if (responseText.includes('Embedding is disabled on tenant level')) {
    error.publicMessage = 'Power BI embedding is disabled on tenant level. Enable service principal embedding/API access in the Power BI admin portal.';
  }
  return error;
}

function readAuthenticatedUser(request) {
  if (!request.session?.appUser) {
    throw authenticationRequiredError();
  }

  return request.session.appUser;
}

function authenticationRequiredError() {
  const error = new Error('Mock user authentication required.');
  error.statusCode = 401;
  error.publicMessage = 'Mock user authentication required.';
  return error;
}

function withPowerBiRole(user) {
  return {
    ...user,
    powerbiRoles: [process.env.POWERBI_RLS_ROLE || 'rls_level']
  };
}

const distPath = path.resolve(__dirname, '../dist');
app.use(express.static(distPath));

app.get('*', (_request, response) => {
  response.sendFile(path.join(distPath, 'index.html'));
});

app.listen(port, () => {
  console.log(`Power BI embedded demo server listening on port ${port}`);
});