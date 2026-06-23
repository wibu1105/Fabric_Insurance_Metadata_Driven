import React, { useState } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import DashboardSummary from '../components/DashboardSummary.jsx';
import PowerBIEmbed from '../components/PowerBIEmbed.jsx';
import ChangePasswordDialog from '../components/ChangePasswordDialog.jsx';
import { dashboards, defaultDashboardId } from '../data/demoConfig.js';

export default function LandingPage({ currentUser, onLogout, onSessionChange }) {
  const [activeDashboardId, setActiveDashboardId] = useState(defaultDashboardId);
  const [isPasswordDialogOpen, setIsPasswordDialogOpen] = useState(false);
  const activeDashboard = dashboards.find((dashboard) => dashboard.id === activeDashboardId) ?? dashboards[0];

  return (
    <div className="app-shell">
      <Header
        currentUser={currentUser}
        dashboards={dashboards}
        activeDashboardId={activeDashboard.id}
        onDashboardChange={setActiveDashboardId}
        onChangePassword={() => setIsPasswordDialogOpen(true)}
        onLogout={onLogout}
      />

      <main className="landing-page">
        <DashboardSummary dashboard={activeDashboard} currentUser={currentUser} />
        <PowerBIEmbed dashboard={activeDashboard} currentUser={currentUser} />
      </main>

      {isPasswordDialogOpen && (
        <ChangePasswordDialog
          onClose={() => setIsPasswordDialogOpen(false)}
          onSessionChange={onSessionChange}
        />
      )}

      <Footer />
    </div>
  );
}
