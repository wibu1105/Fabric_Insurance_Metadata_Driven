import React from 'react';

export default function DashboardSummary({ dashboard, currentUser }) {
  return (
    <section className="summary-grid" aria-labelledby="dashboard-title">
      <div className="summary-card summary-card--main">
        <p className="eyebrow">Selected dashboard</p>
        <h1 id="dashboard-title">{dashboard.title}</h1>
        <p>{dashboard.summary}</p>
      </div>

      <div className="summary-card">
        <p className="eyebrow">Demo identity</p>
        <h2>{currentUser.userMail}</h2>
        <p>{currentUser.role} - RLS level {currentUser.rlsLevel}</p>
        <p className="muted">RLS username: {currentUser.effectiveUsername}</p>
        <p className="muted">Effective identity: {currentUser.powerbiUsername}</p>
        <p className="muted">Access value: {currentUser.accessValue ?? 'ALL'}</p>
      </div>
    </section>
  );
}
