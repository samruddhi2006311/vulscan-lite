import React, { useState, useEffect } from 'react';
import ScanForm from './components/ScanForm';
import ReportCard from './components/ReportCard';
import History from './components/History';
import './App.css';

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [jobId, setJobId] = useState(null);
  const [tab, setTab] = useState('scan');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className="app-wrapper">
      <div className="app">

        {/* Header */}
        <header className="header">
          <div className="header-left">
            <div className="header-tag">Security Analysis Tool</div>
            <h1>VULN<span>SCAN</span> LITE</h1>
            <p className="header-sub">
               passive recon · header analysis · ssl inspection · cms detection
            </p>
          </div>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            <span className="toggle-icon">{theme === 'dark' ? '☀️' : '🌙'}</span>
          </button>
        </header>

        {/* Disclaimer */}
        <div className="disclaimer">
          ⚠ Authorized use only. Scan only systems you own or have permission to test.
        </div>

        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab-btn ${tab === 'scan' ? 'active' : ''}`}
            onClick={() => setTab('scan')}
          >
            🔍 Scanner
          </button>
          <button
            className={`tab-btn ${tab === 'history' ? 'active' : ''}`}
            onClick={() => setTab('history')}
          >
            📋 History
          </button>
        </div>

        {/* Scanner Tab */}
        {tab === 'scan' && (
          <>
            <ScanForm
              setReport={setReport}
              setLoading={setLoading}
              setError={setError}
              setJobId={setJobId}
              loading={loading}
            />

            {loading && (
              <div className="loading-card">
                <div className="scan-animation">
                  <div className="scan-ring"></div>
                  <div className="scan-ring"></div>
                  <div className="scan-ring"></div>
                  <div className="scan-dot"></div>
                </div>
                <p className="loading-text">
                  SCANNING TARGET
                  <span className="dots">
                    <span>.</span><span>.</span><span>.</span>
                  </span>
                </p>
                <p className="loading-sub">
                   analyzing headers · ssl · cms · scoring
                </p>
              </div>
            )}

            {error && (
              <div className="error-card">✗ ERROR — {error}</div>
            )}

            {report && !loading && (
              <ReportCard report={report} jobId={jobId} />
            )}
          </>
        )}

        {/* History Tab */}
        {tab === 'history' && <History />}

      </div>
    </div>
  );
}

export default App;