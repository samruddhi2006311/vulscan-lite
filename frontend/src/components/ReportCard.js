import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const API_URL = 'https://vulscan-lite.onrender.com';

const fixes = {
  'Content-Security-Policy': `# Nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;

# Apache
Header always set Content-Security-Policy "default-src 'self'"`,

  'X-Frame-Options': `# Nginx
add_header X-Frame-Options "SAMEORIGIN" always;

# Apache
Header always set X-Frame-Options "SAMEORIGIN"`,

  'Strict-Transport-Security': `# Nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"`
};

function ReportCard({ report, jobId }) {
  const maxScore = 60;
  const normalizedScore = Math.max(0, Math.min(100,
    ((report.total_score + 30) / (maxScore + 30)) * 100
  ));

  const gradeColor = {
    'A': '#00ff88',
    'B': '#00b4ff',
    'C': '#ffa502',
    'D': '#ff4757'
  }[report.grade] || '#8892a4';

  const gradeLabel = {
    'A': 'SECURE',
    'B': 'MODERATE',
    'C': 'AT RISK',
    'D': 'VULNERABLE'
  }[report.grade] || 'UNKNOWN';

  return (
    <div className="report">

      {/* Grade Section */}
      <div className="grade-section" style={{ borderColor: `${gradeColor}25` }}>
        <div className="grade-circle">
          <CircularProgressbar
            value={normalizedScore}
            text={report.grade}
            styles={buildStyles({
              textSize: '36px',
              textColor: gradeColor,
              pathColor: gradeColor,
              trailColor: 'rgba(255,255,255,0.05)',
              strokeLinecap: 'round',
            })}
          />
        </div>
        <div className="grade-info">
          <h2>SECURITY REPORT</h2>
          <div className="grade-url">⟩ {report.url}</div>
          <div className="grade-score">
            Score: <span>{report.total_score}</span> pts &nbsp;|&nbsp; Status:{' '}
            <span style={{ color: gradeColor }}>{gradeLabel}</span>
          </div>

          {/* PDF Download Button */}
          {jobId && (
            <a
              href={`${API_URL}/api/scan/pdf/${jobId}`}
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                marginTop: '14px',
                padding: '10px 18px',
                background: 'var(--accent-dim)',
                border: '1px solid var(--accent-border)',
                borderRadius: '6px',
                color: 'var(--accent)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.78rem',
                textDecoration: 'none',
                letterSpacing: '1px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'var(--accent)';
                e.currentTarget.style.color = '#0a0e1a';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'var(--accent-dim)';
                e.currentTarget.style.color = 'var(--accent)';
              }}
            >
              ⬇ Download PDF Report
            </a>
          )}
        </div>
      </div>

      {/* Stats Row */}
      <div className="stats-row">

        <div className="stat-card">
          <div className="stat-icon">🔐</div>
          <div className="stat-label">SSL Certificate</div>
          <div className={`stat-value ${report.ssl.is_valid ? 'good' : 'bad'}`}>
            {report.ssl.is_valid ? 'VALID' : 'INVALID'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-label">Cert Expires</div>
          <div className={`stat-value ${report.ssl.days_left > 30 ? 'good' : 'warn'}`}>
            {report.ssl.days_left ? `${report.ssl.days_left}d` : 'N/A'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🖥️</div>
          <div className="stat-label">CMS Detected</div>
          <div className={`stat-value ${report.cms.cms_name ? 'warn' : 'good'}`}>
            {report.cms.cms_name || 'NONE'}
          </div>
        </div>

      </div>

      {/* CMS Warning */}
      {report.cms.cms_name && (
        <div className="cms-card">
          <div className="cms-title">⚠ CMS DETECTED</div>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
            {report.cms.cms_name}
            {report.cms.cms_version && ` — version ${report.cms.cms_version}`}
          </p>
          {report.cms.warnings.map((w, i) => (
            <div key={i} className="cms-warning">⟩ {w}</div>
          ))}
        </div>
      )}

      {/* Checks Grid */}
      <div className="checks-grid">

        {/* Passed */}
        <div className="checks-card passed">
          <div className="checks-title passed">✓ PASSED</div>
          {report.headers.passed.length === 0 ? (
            <div className="check-item" style={{ color: 'var(--text-muted)', background: 'transparent', border: '1px dashed var(--border)' }}>
              No checks passed
            </div>
          ) : (
            report.headers.passed.map((h, i) => (
              <div key={i} className="check-item passed">✓ {h}</div>
            ))
          )}
        </div>

        {/* Failed */}
        <div className="checks-card failed">
          <div className="checks-title failed">✗ FAILED</div>
          {report.headers.failed.length === 0 ? (
            <div className="check-item" style={{ color: 'var(--accent)', background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
              All checks passed!
            </div>
          ) : (
            report.headers.failed.map((h, i) => (
              <div key={i} className="check-item failed">✗ {h}</div>
            ))
          )}
        </div>

      </div>

      {/* Fixes */}
      {report.headers.failed.length > 0 && (
        <div className="fixes-card">
          <div className="fixes-title">⟩ REMEDIATION GUIDE</div>
          {report.headers.failed.map((header, i) => (
            fixes[header] && (
              <div key={i} className="fix-item">
                <div className="fix-header">
                  ⟩ Fix: {header}
                </div>
                <pre className="fix-code">{fixes[header]}</pre>
              </div>
            )
          ))}
        </div>
      )}

    </div>
  );
}

export default ReportCard;