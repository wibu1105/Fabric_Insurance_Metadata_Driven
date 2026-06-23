import React, { useEffect, useState } from 'react';
import {
  getCurrentUser,
  getMicrosoftAuthStatus,
  loginUser,
  logoutUser,
  redirectToMicrosoftLogin
} from './services/authApi.js';
import LoginPage from './pages/LoginPage.jsx';
import LandingPage from './pages/LandingPage.jsx';

function AuthLoading({ message }) {
  return (
    <main className="login-page">
      <section className="login-shell" aria-label="Authentication status">
        <div className="login-hero">
          <p className="eyebrow">CarPro</p>
          <h1>Preparing Analytics Demo</h1>
          <p className="hero-copy">{message}</p>
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [session, setSession] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [authMessage, setAuthMessage] = useState('Checking Microsoft presenter session...');

  useEffect(() => {
    let cancelled = false;

    async function bootstrapAuth() {
      try {
        const microsoftStatus = await getMicrosoftAuthStatus();
        if (cancelled) return;

        if (!microsoftStatus.microsoftAuthenticated) {
          setAuthMessage('Redirecting to Microsoft sign-in...');
          redirectToMicrosoftLogin();
          return;
        }

        const currentSession = await getCurrentUser();
        if (!cancelled) {
          setSession(currentSession);
          setIsAuthReady(true);
        }
      } catch (error) {
        if (!cancelled) {
          setAuthMessage(error.message || 'Unable to start authentication.');
          setIsAuthReady(true);
        }
      }
    }

    bootstrapAuth();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = async (credentials) => {
    const nextSession = await loginUser(credentials);
    setSession(nextSession);
  };

  const updateSession = (nextSession) => {
    setSession(nextSession);
  };

  const logout = async () => {
    await logoutUser();
    setSession(null);
  };

  if (!isAuthReady) {
    return <AuthLoading message={authMessage} />;
  }

  if (!session) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <LandingPage
      currentUser={session.user}
      onLogout={logout}
      onSessionChange={updateSession}
    />
  );
}
