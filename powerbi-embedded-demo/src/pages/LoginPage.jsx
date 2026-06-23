import React, { useEffect, useState } from 'react';
import BrandMark from '../components/BrandMark.jsx';
import { getLoginUsers } from '../services/authApi.js';

export default function LoginPage({ onLogin }) {
  const [userMail, setUserMail] = useState('');
  const [password, setPassword] = useState('');
  const [warehouseUsers, setWarehouseUsers] = useState([]);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    getLoginUsers()
      .then(({ users }) => {
        if (!cancelled) {
          setWarehouseUsers(users ?? []);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setWarehouseUsers([]);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const submitLogin = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await onLogin({ userMail, password });
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-shell" aria-labelledby="login-title">
        <div className="login-hero">
          <BrandMark variant="red" />
          <p className="eyebrow">NashTech Demo Portal</p>
          <h1 id="login-title">CarPro Embedded Analytics Demo</h1>
          <p className="hero-copy">
            Sign in with your warehouse user mail to open the RLS-filtered dashboard view.
          </p>
        </div>

        <form className="login-panel" aria-label="Sign in" onSubmit={submitLogin}>
          <div className="field-group">
            <label htmlFor="user-mail">User mail</label>
            <input
              id="user-mail"
              name="userMail"
              autoComplete="username"
              value={userMail}
              onChange={(event) => setUserMail(event.target.value)}
              placeholder="User mail"
            />
          </div>

          <div className="field-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
            />
          </div>

          {error && <p className="form-error" role="alert">{error}</p>}

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>

          {warehouseUsers.length > 0 && (
            <section className="warehouse-users" aria-label="Warehouse users">
              <p className="eyebrow">Warehouse users</p>
              <div className="warehouse-user-list">
                {warehouseUsers.map((user) => (
                  <button
                    key={user.userMail}
                    className="warehouse-user-button"
                    type="button"
                    onClick={() => {
                      setUserMail(user.userMail);
                      setPassword(user.password);
                    }}
                  >
                    <span>{user.userMail}</span>
                    <small>{user.effectiveUsername} - Level {user.rlsLevel} - {user.accessValue ?? 'ALL'}</small>
                  </button>
                ))}
              </div>
            </section>
          )}
        </form>
      </section>
    </main>
  );
}
