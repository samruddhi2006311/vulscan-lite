import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'https://vulscan-lite.onrender.com';

const gradeColor = {
  'A': '#00ff88',
  'B': '#00b4ff',
  'C': '#ffa502',
  'D': '#ff4757'
};

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/api/history`);
      setHistory(res.data);
      setError(null);
    } catch (err) {
      setError('Could not load history. Make sure Flask is running.');
    }
    setLoading(false);
  };

  const clearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all scan history?')) return;
    try {
      await axios.delete(`${API_URL}/api/history`);
      setHistory([]);
    } catch (err) {
      setError('Could not clear history.');
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  if (loading) return (
    <div className="history-card">
      <p className="history-loading">
        ⟩ Loading scan history
        <span className="dots">
          <span>.</span><span>.</span><span>.</span>
        </span>
      </p>
    </div>
  );

  if (error) return (
    <div className="error-card">✗ {error}</div>
  );

  if (history.length === 0) return (
    <div className="history-card">
      <div className="history-empty">
        <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📭</div>
        <p>No scan history yet.</p>
        <p style={{ fontSize: '0.75rem', marginTop: '6px' }}>
          Run your first scan to see results here.
        </p>
      </div>
    </div>
  );

  return (
    <div className="history-card">

      {/* Header */}
      <div className="history-header">
        <div className="history-title">⟩ SCAN HISTORY</div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span className="history-count">{history.length} scans</span>
          <button className="clear-btn" onClick={clearHistory}>
            🗑 Clear All
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>TARGET URL</th>
              <th>GRADE</th>
              <th>SCORE</th>
              <th>SSL</th>
              <th>CMS</th>
              <th>DATE</th>
              <th>PDF</th>
            </tr>
          </thead>
          <tbody>
            {history.map((scan) => (
              <tr key={scan.id} className="history-row">
                <td className="history-url">
                  <span title={scan.url}>
                    {scan.url.length > 35
                      ? scan.url.slice(0, 35) + '...'
                      : scan.url}
                  </span>
                </td>
                <td>
                  <span
                    className="history-grade"
                    style={{ color: gradeColor[scan.grade] || '#8892a4' }}
                  >
                    {scan.grade}
                  </span>
                </td>
                <td className="history-score">{scan.score}</td>
                <td>
                  <span style={{ color: scan.ssl_valid ? '#00ff88' : '#ff4757' }}>
                    {scan.ssl_valid ? '✓' : '✗'}
                  </span>
                </td>
                <td className="history-cms">
                  {scan.cms_name || '—'}
                </td>
                <td className="history-date">
                  {scan.scanned_at}
                </td>
                <td>
                  <a
                    href={`${API_URL}/api/scan/pdf/${scan.job_id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="history-pdf-btn"
                    title="Download PDF Report"
                  >
                    ⬇
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default History;