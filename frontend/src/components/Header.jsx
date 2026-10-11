import React from 'react';

export default function Header({ currentView, setView, aiStatus, activeTrip }) {
  return (
    <header className="app-header">
      <div className="header-top">
        <div className="brand">
          <div className="brand-icon">🌿</div>
          <div>
            <h1 className="brand-title">ErrandQuest</h1>
            <p className="brand-tagline">One Trip. Everything Done.</p>
          </div>
        </div>

        <div className="ai-status-pill" title={aiStatus?.note || 'AI Extraction Engine'}>
          <span className={`status-dot ${aiStatus?.available ? 'online' : 'heuristic'}`}></span>
          <span className="status-label">
            {aiStatus?.available ? `🤖 Ollama (${aiStatus.default_model || 'Local'})` : '⚡ Built-in Fast NLP'}
          </span>
        </div>
      </div>

      <nav className="view-nav">
        <button
          className={`nav-btn ${currentView === 'inbox' ? 'active' : ''}`}
          onClick={() => setView('inbox')}
        >
          <span className="nav-icon">📋</span>
          <span>1. Inbox</span>
        </button>

        <button
          className={`nav-btn ${currentView === 'plan' ? 'active' : ''}`}
          onClick={() => setView('plan')}
        >
          <span className="nav-icon">🗺️</span>
          <span>2. Plan</span>
        </button>

        <button
          className={`nav-btn ${currentView === 'departure' ? 'active' : ''}`}
          onClick={() => setView('departure')}
        >
          <span className="nav-icon">🎒</span>
          <span>3. Departure</span>
        </button>

        <button
          className={`nav-btn ${currentView === 'trip' ? 'active' : ''} ${activeTrip ? 'has-active' : ''}`}
          onClick={() => setView('trip')}
        >
          <span className="nav-icon">{activeTrip ? '🚶‍♂️' : '📍'}</span>
          <span>4. Outing {activeTrip && <span className="active-badge">Live</span>}</span>
        </button>
      </nav>
    </header>
  );
}
