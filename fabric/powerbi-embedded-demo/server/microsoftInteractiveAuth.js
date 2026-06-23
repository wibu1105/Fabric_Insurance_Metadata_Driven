import crypto from 'node:crypto';
import { ConfidentialClientApplication } from '@azure/msal-node';

const DEFAULT_POWERBI_SCOPES = ['https://analysis.windows.net/powerbi/api/.default'];
const TOKEN_EXPIRY_SAFETY_MS = 5 * 60 * 1000;

export function readPowerBiScopes() {
  return String(process.env.POWERBI_AUTH_SCOPES ?? DEFAULT_POWERBI_SCOPES.join(' '))
    .split(/[\s,]+/)
    .map((scope) => scope.trim())
    .filter(Boolean);
}

export function createInteractiveMsalClient() {
  const tenantId = readRequiredEnv('TENANT_ID');
  const clientId = readClientIdEnv('CLIENT_ID');
  const clientSecret = readRequiredEnv('CLIENT_SECRET');

  return new ConfidentialClientApplication({
    auth: {
      clientId,
      authority: `https://login.microsoftonline.com/${tenantId}`,
      clientSecret
    }
  });
}

export function resolveMicrosoftRedirectUri(request) {
  if (process.env.MICROSOFT_REDIRECT_URI) {
    return process.env.MICROSOFT_REDIRECT_URI;
  }

  return `${request.protocol}://${request.get('host')}/api/auth/microsoft/callback`;
}

export async function createMicrosoftLoginUrl(request) {
  const state = crypto.randomUUID();
  request.session.microsoftAuthState = state;

  return createInteractiveMsalClient().getAuthCodeUrl({
    scopes: readPowerBiScopes(),
    redirectUri: resolveMicrosoftRedirectUri(request),
    state,
    prompt: 'select_account'
  });
}

export async function acquireMicrosoftTokenFromCode(request) {
  if (request.query?.error) {
    throw publicAuthError(
      `Microsoft sign-in failed: ${request.query.error_description ?? request.query.error}`,
      401
    );
  }

  const code = request.query?.code;
  if (!code) {
    throw publicAuthError('Microsoft sign-in callback did not include an authorization code.', 400);
  }

  const expectedState = request.session.microsoftAuthState;
  if (expectedState && request.query?.state !== expectedState) {
    throw publicAuthError('Microsoft sign-in state validation failed.', 400);
  }

  delete request.session.microsoftAuthState;

  return createInteractiveMsalClient().acquireTokenByCode({
    code,
    scopes: readPowerBiScopes(),
    redirectUri: resolveMicrosoftRedirectUri(request)
  });
}

export function storeMicrosoftToken(session, tokenResponse) {
  if (!tokenResponse?.accessToken) {
    throw publicAuthError('Microsoft sign-in did not return an access token.', 401);
  }

  session.microsoftAuth = {
    accessToken: tokenResponse.accessToken,
    expiresOn: tokenResponse.expiresOn?.toISOString?.() ?? null,
    accountUsername: tokenResponse.account?.username ?? null
  };
}

export function hasValidMicrosoftToken(session, now = new Date()) {
  const token = session?.microsoftAuth?.accessToken;
  const expiresOn = session?.microsoftAuth?.expiresOn;
  if (!token || !expiresOn) {
    return false;
  }

  const expiryMs = new Date(expiresOn).getTime();
  if (!Number.isFinite(expiryMs)) {
    return false;
  }

  return expiryMs - now.getTime() > TOKEN_EXPIRY_SAFETY_MS;
}

export function readMicrosoftAccessToken(request, now = new Date()) {
  if (!hasValidMicrosoftToken(request.session, now)) {
    throw publicAuthError('Microsoft admin login required.', 401);
  }

  return request.session.microsoftAuth.accessToken;
}

export function microsoftStatus(session, now = new Date()) {
  return {
    microsoftAuthenticated: hasValidMicrosoftToken(session, now),
    accountUsername: session?.microsoftAuth?.accountUsername ?? null
  };
}

function readRequiredEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw configurationError(`Missing required environment variable: ${name}`);
  }
  return value;
}

function readClientIdEnv(name) {
  const value = readRequiredEnv(name);
  if (!isGuid(value)) {
    const hint = value.includes('~')
      ? ' It looks like CLIENT_ID may contain a client secret value. Use the Application (client) ID from the app registration Overview page, and use the secret Value for CLIENT_SECRET.'
      : '';
    throw configurationError(`Invalid ${name}. CLIENT_ID must be the Application (client) ID GUID.${hint}`);
  }
  return value;
}

function isGuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
}

function configurationError(message) {
  const error = new Error(message);
  error.publicMessage = message;
  return error;
}

function publicAuthError(message, statusCode) {
  const error = new Error(message);
  error.publicMessage = message;
  error.statusCode = statusCode;
  return error;
}
