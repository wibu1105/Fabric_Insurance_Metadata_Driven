import crypto from 'node:crypto';

const SESSION_TTL_SECONDS = 8 * 60 * 60;

export function createSessionToken(user) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: user.userMail,
    userMail: user.userMail,
    effectiveUsername: user.userMail,
    role: user.role,
    rlsLevel: user.rlsLevel,
    accessValue: user.accessValue,
    powerbiUsername: user.userMail,
    iat: now,
    exp: now + SESSION_TTL_SECONDS
  };

  const encodedPayload = base64UrlEncode(JSON.stringify(payload));
  const signature = sign(encodedPayload);
  return `${encodedPayload}.${signature}`;
}

export function verifySessionToken(token) {
  if (!token || typeof token !== 'string') {
    throw authError('Missing authentication token.');
  }

  const [encodedPayload, signature] = token.split('.');
  if (!encodedPayload || !signature) {
    throw authError('Invalid authentication token.');
  }

  const expectedSignature = sign(encodedPayload);
  if (!timingSafeEqual(signature, expectedSignature)) {
    throw authError('Invalid authentication token.');
  }

  const payload = JSON.parse(Buffer.from(encodedPayload, 'base64url').toString('utf8'));
  if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) {
    throw authError('Authentication token expired.');
  }

  return {
    userMail: payload.userMail,
    effectiveUsername: payload.userMail,
    role: payload.role,
    rlsLevel: payload.rlsLevel,
    accessValue: payload.accessValue,
    powerbiUsername: payload.userMail
  };
}

export function readBearerToken(request) {
  const authorization = request.headers.authorization;
  if (!authorization?.startsWith('Bearer ')) {
    return null;
  }
  return authorization.slice('Bearer '.length).trim();
}

function sign(value) {
  return crypto.createHmac('sha256', readSessionSecret()).update(value).digest('base64url');
}

function timingSafeEqual(left, right) {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  return leftBuffer.length === rightBuffer.length && crypto.timingSafeEqual(leftBuffer, rightBuffer);
}

function base64UrlEncode(value) {
  return Buffer.from(value).toString('base64url');
}

function readSessionSecret() {
  const secret = process.env.SESSION_SECRET || process.env.CLIENT_SECRET;
  if (!secret) {
    throw new Error('Missing required environment variable: SESSION_SECRET');
  }
  return secret;
}

function authError(message) {
  const error = new Error(message);
  error.statusCode = 401;
  error.publicMessage = message;
  return error;
}
