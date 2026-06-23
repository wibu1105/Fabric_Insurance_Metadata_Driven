import React from 'react';
import BrandMark from './BrandMark.jsx';

export default function Header({ currentUser, dashboards, activeDashboardId, onDashboardChange, onChangePassword, onLogout }) {
  return (
    <header className="site-header">
      <div className="header-brand">
        <BrandMark />
        <div>
          <p className="eyebrow">CarPro</p>
          <p className="header-title">Embedded Analytics Demo</p>
        </div>
      </div>

      <nav className="header-actions" aria-label="Dashboard navigation">
        <div className="dashboard-tabs" role="group" aria-label="Switch dashboard">
          {dashboards.map((dashboard) => (
            <button
              key={dashboard.id}
              className={dashboard.id === activeDashboardId ? 'tab-button tab-button--active' : 'tab-button'}
              type="button"
              onClick={() => onDashboardChange(dashboard.id)}
            >
              {dashboard.shortTitle}
            </button>
          ))}
        </div>
        <div className="user-chip">{currentUser.userMail} - {currentUser.role}</div>
        <button className="ghost-button" type="button" onClick={onChangePassword}>
          Change password
        </button>
        <button className="ghost-button" type="button" onClick={onLogout}>
          Logout
        </button>
      </nav>
    </header>
  );
}
