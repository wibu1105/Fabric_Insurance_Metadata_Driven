import React from 'react';
export default function DashboardSelector({ dashboards, activeDashboardId, onDashboardChange }) {
  return (
    <section className="dashboard-selector" aria-label="Available dashboards">
      {dashboards.map((dashboard) => (
        <button
          key={dashboard.id}
          className={dashboard.id === activeDashboardId ? 'dashboard-card dashboard-card--active' : 'dashboard-card'}
          type="button"
          onClick={() => onDashboardChange(dashboard.id)}
        >
          <span>{dashboard.shortTitle}</span>
          <small>{dashboard.audience}</small>
        </button>
      ))}
    </section>
  );
}
