import React, { useEffect, useState } from 'react';
import { PowerBIEmbed as PowerBIEmbedFrame } from 'powerbi-client-react';
import { models } from 'powerbi-client';
import { getEmbedConfig } from '../services/embedApi.js';

function EmbedPlaceholder({ dashboard, currentUser, status }) {
  return (
    <div className="embed-placeholder">
      <div>
        <p className="eyebrow">Demo embed frame</p>
        <p className="embed-placeholder-title">{dashboard.title}</p>
        <p>
          {status === 'error'
            ? 'The live Power BI embed configuration is not available. The page remains ready for deployment once report IDs and service-principal values are supplied.'
            : 'Live embedding is prepared through the backend API. In local demo mode, this placeholder represents the Power BI iframe area.'}
        </p>
      </div>
      <dl className="embed-details">
        <div>
          <dt>Dashboard key</dt>
          <dd>{dashboard.embedKey}</dd>
        </div>
        <div>
          <dt>RLS username</dt>
          <dd>{currentUser.powerbiUsername}</dd>
        </div>
        <div>
          <dt>Power BI role</dt>
          <dd>{currentUser.powerbiRoles.join(', ')}</dd>
        </div>
      </dl>
    </div>
  );
}

export default function PowerBIEmbed({ dashboard, currentUser }) {
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('Preparing embed configuration...');
  const [embedConfig, setEmbedConfig] = useState(null);
  const [reportInstance, setReportInstance] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setStatus('loading');
      setMessage('Preparing embed configuration...');
      setEmbedConfig(null);
      setReportInstance(null);

      try {
        const config = await getEmbedConfig({ dashboardId: dashboard.id });
        if (cancelled) return;

        if (!config.embedToken || config.mode === 'demo') {
          setStatus('demo');
          setMessage(config.message ?? 'Demo mode is active.');
          return;
        }

        setEmbedConfig({
          type: 'report',
          id: config.reportId,
          embedUrl: config.embedUrl,
          accessToken: config.embedToken,
          tokenType: models.TokenType.Embed,
          permissions: models.Permissions.Read,
          settings: {
            panes: {
              filters: { visible: false },
              pageNavigation: { visible: true }
            },
            background: models.BackgroundType.Transparent
          }
        });
        setStatus('embedded');
        setMessage('Power BI report embedded.');
      } catch (error) {
        if (cancelled) return;
        setStatus('error');
        setMessage(error.message);
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
      setReportInstance(null);
    };
  }, [dashboard, currentUser]);

  async function handleFitToPage() {
    if (!reportInstance) {
      return;
    }

    await reportInstance.updateSettings({
      layoutType: models.LayoutType.Custom,
      customLayout: {
        displayOption: models.DisplayOption.FitToPage
      }
    });
  }

  return (
    <section className="embed-section" aria-label="Power BI embedded dashboard">
      <div className="embed-toolbar">
        <div>
          <p className="eyebrow">Power BI Embed</p>
          <h2>{status === 'embedded' ? 'Live dashboard' : 'Dashboard preview'}</h2>
        </div>
        <div className="embed-toolbar-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={handleFitToPage}
            disabled={!reportInstance || status !== 'embedded'}
          >
            Fit to Page
          </button>
          <span className={`status-pill status-pill--${status}`}>{message}</span>
        </div>
      </div>
      <div className="powerbi-container">
        {embedConfig ? (
          <PowerBIEmbedFrame
            embedConfig={embedConfig}
            cssClassName={status === 'embedded' ? 'powerbi-frame powerbi-frame--active' : 'powerbi-frame'}
            getEmbeddedComponent={(embeddedReport) => setReportInstance(embeddedReport)}
          />
        ) : (
          <div className="powerbi-frame" aria-hidden="true" />
        )}
        {status !== 'embedded' && <EmbedPlaceholder dashboard={dashboard} currentUser={currentUser} status={status} />}
      </div>
    </section>
  );
}
