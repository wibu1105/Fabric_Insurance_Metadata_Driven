export async function getMicrosoftAuthStatus() {
  const response = await fetch('/api/auth/microsoft/status', {
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error((await response.text()) || 'Unable to check Microsoft sign-in status.');
  }

  return response.json();
}

export function redirectToMicrosoftLogin() {
  window.location.assign('/api/auth/microsoft/login');
}

export async function getCurrentUser() {
  const response = await fetch('/api/auth/me', {
    credentials: 'include'
  });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error((await response.text()) || 'Unable to read current session.');
  }

  return response.json();
}

export async function loginUser({ userMail, password }) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userMail, password })
  });

  if (!response.ok) {
    throw new Error((await response.text()) || 'Login failed.');
  }

  return response.json();
}

export async function logoutUser() {
  await fetch('/api/auth/logout', {
    method: 'POST',
    credentials: 'include'
  });
}

export async function getLoginUsers() {
  const response = await fetch('/api/auth/users', { credentials: 'include' });

  if (!response.ok) {
    throw new Error((await response.text()) || 'Unable to read warehouse users.');
  }

  return response.json();
}

export async function changePassword({ currentPassword, newPassword }) {
  const response = await fetch('/api/auth/change-password', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ currentPassword, newPassword })
  });

  if (!response.ok) {
    throw new Error((await response.text()) || 'Password change failed.');
  }

  return response.json();
}
