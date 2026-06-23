import sql from 'mssql';
import { ConfidentialClientApplication } from '@azure/msal-node';

const APP_USERS_TABLE = '[web].[app_users_rls]';
const USER_MAIL_COLUMN = sqlIdentifier(process.env.APP_USERS_USER_MAIL_COLUMN || 'user_mail');

export async function authenticateAppUser({ userMail, password }) {
  const normalizedUserMail = normalizeLogin(userMail);
  if (!normalizedUserMail || !password) {
    throw authError('Invalid username or password.');
  }

  const row = await getAppUserRow(normalizedUserMail);
  if (!row || row.password !== password) {
    throw authError('Invalid username or password.');
  }

  return toSessionUser(row);
}

export async function listAppUsers() {
  const pool = await connectWarehouse();
  try {
    const result = await pool
      .request()
      .query(`
        SELECT
          CAST(${USER_MAIL_COLUMN} AS nvarchar(128)) AS user_mail,
          CAST([rls_level] AS int) AS rls_level,
          CAST([access_value] AS nvarchar(256)) AS access_value
        FROM ${APP_USERS_TABLE}
        ORDER BY [rls_level], ${USER_MAIL_COLUMN}
      `);

    return result.recordset.map(toPublicUser);
  } finally {
    await pool.close();
  }
}

export async function changeAppUserPassword({ userMail, currentPassword, newPassword }) {
  const normalizedUserMail = normalizeLogin(userMail);
  if (!currentPassword || !newPassword || newPassword.length < 4) {
    throw authError('Password must be at least 4 characters.');
  }

  const row = await getAppUserRow(normalizedUserMail);
  if (!row || row.password !== currentPassword) {
    throw authError('Current password is incorrect.');
  }

  const pool = await connectWarehouse();
  try {
    await pool
      .request()
      .input('userMail', sql.NVarChar(128), row.user_mail)
      .input('newPassword', sql.NVarChar(512), newPassword)
      .query(`UPDATE ${APP_USERS_TABLE} SET [password] = @newPassword WHERE ${USER_MAIL_COLUMN} = @userMail`);
  } finally {
    await pool.close();
  }

  return toSessionUser({ ...row, password: newPassword });
}

async function getAppUserRow(userMail) {
  const pool = await connectWarehouse();
  try {
    const result = await pool
      .request()
      .input('userMail', sql.NVarChar(128), userMail)
      .query(`
        SELECT TOP (1)
          CAST(${USER_MAIL_COLUMN} AS nvarchar(128)) AS user_mail,
          CAST([password] AS nvarchar(512)) AS [password],
          CAST([rls_level] AS int) AS rls_level,
          CAST([access_value] AS nvarchar(256)) AS access_value
        FROM ${APP_USERS_TABLE}
        WHERE UPPER(CAST(${USER_MAIL_COLUMN} AS nvarchar(128))) = @userMail
          OR UPPER(${userMailPrefixExpression()}) = @userMail
          OR UPPER(CAST([access_value] AS nvarchar(256))) = @userMail
      `);

    return result.recordset[0] ?? null;
  } finally {
    await pool.close();
  }
}

async function connectWarehouse() {
  const accessToken = await getWarehouseAccessToken();
  const pool = new sql.ConnectionPool({
    server: readRequiredEnv('AUDIT_WAREHOUSE_SQL_ENDPOINT'),
    database: readRequiredEnv('AUDIT_WAREHOUSE_NAME'),
    authentication: {
      type: 'azure-active-directory-access-token',
      options: {
        token: accessToken
      }
    },
    options: {
      encrypt: true,
      trustServerCertificate: false
    }
  });

  return pool.connect();
}

async function getWarehouseAccessToken() {
  const tenantId = readRequiredEnv('TENANT_ID');
  const clientId = readRequiredEnv('CLIENT_ID');
  const clientSecret = readRequiredEnv('CLIENT_SECRET');

  const client = new ConfidentialClientApplication({
    auth: {
      clientId,
      authority: `https://login.microsoftonline.com/${tenantId}`,
      clientSecret
    }
  });

  const result = await client.acquireTokenByClientCredential({
    scopes: ['https://database.windows.net/.default']
  });

  if (!result?.accessToken) {
    throw new Error('Unable to acquire Fabric Warehouse SQL access token.');
  }

  return result.accessToken;
}

function toSessionUser(row) {
  const userMail = normalizeUserMail(row.user_mail);
  const effectiveUsername = toEffectiveUsername(row);
  const rlsLevel = Number(row.rls_level);

  return {
    id: userMail,
    userMail,
    username: userMail,
    effectiveUsername,
    role: roleLabel(rlsLevel),
    rlsLevel,
    accessValue: row.access_value ?? null,
    powerbiUsername: userMail
  };
}

function toPublicUser(row) {
  const userMail = normalizeUserMail(row.user_mail);
  const effectiveUsername = toEffectiveUsername(row);
  const rlsLevel = Number(row.rls_level);

  return {
    id: userMail,
    userMail,
    username: userMail,
    effectiveUsername,
    role: roleLabel(rlsLevel),
    rlsLevel,
    accessValue: row.access_value ?? null,
    powerbiUsername: userMail
  };
}

function toEffectiveUsername(row) {
  return normalizeLogin(row.access_value ?? stripMailSuffix(row.user_mail));
}

function roleLabel(rlsLevel) {
  if (rlsLevel === 1) return 'Admin';
  if (rlsLevel === 2) return 'Agent';
  if (rlsLevel === 3) return 'Provider';
  return 'Restricted User';
}

function normalizeLogin(value) {
  return String(value ?? '').trim().toUpperCase();
}

function normalizeUserMail(value) {
  return String(value ?? '').trim();
}

function stripMailSuffix(value) {
  return String(value ?? '').split('@')[0];
}

function readRequiredEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function sqlIdentifier(name) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) {
    throw new Error(`Invalid SQL identifier configured: ${name}`);
  }
  return `[${name}]`;
}

function userMailPrefixExpression() {
  const userMail = `CAST(${USER_MAIL_COLUMN} AS nvarchar(128))`;
  return `
    CASE
      WHEN CHARINDEX('@', ${userMail}) > 0 THEN LEFT(${userMail}, CHARINDEX('@', ${userMail}) - 1)
      ELSE ${userMail}
    END
  `;
}

function authError(message) {
  const error = new Error(message);
  error.statusCode = 401;
  error.publicMessage = message;
  return error;
}
