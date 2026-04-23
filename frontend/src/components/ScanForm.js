import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://vulscan-lite.onrender.com';

function isValidUrl(value) {
  if (!value.trim()) return null;
  const pattern = /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/.*)?$/;
  return pattern.test(value.trim());
}

function ScanForm({ setReport, setLoading, setError, setJobId, loading }) {
  const [url, setUrl] = useState('');
  const [touched, setTouched] = useState(false);

  const validity = isValidUrl(url);

  const getBorderColor = () => {
    if (!touched || url === '') return undefined;
    if (validity === true) return 'var(--accent)';
    if (validity === false) return 'var(--danger)';
    return undefined;
  };

  const handleScan = async () => {
    setTouched(true);
    if (!url.trim()) {
      setError('Target URL required. Enter a domain to analyze.');
      return;
    }
    if (!isValidUrl(url)) {
      setError('Invalid URL. Try: example.com or https://example.com');
      return;
    }

    setError(null);
    setReport(null);
    setJobId(null);
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/scan`, { url });
      const jobId = response.data.job_id;
      setJobId(jobId);

      const interval = setInterval(async () => {
        try {
          const statusRes = await axios.get(`${API_URL}/api/scan/status/${jobId}`);
          if (statusRes.data.status === 'completed') {
            clearInterval(interval);
            setReport(statusRes.data.result);
            setLoading(false);
          } else if (statusRes.data.status === 'failed') {
            clearInterval(interval);
            setError('Scan failed. Target may be unreachable.');
            setLoading(false);
          }
        } catch (err) {
          clearInterval(interval);
          setError('Connection lost while polling scan status.');
          setLoading(false);
        }
      }, 2000);

    } catch (err) {
      setError('Cannot reach backend. Make sure Flask is running on port 5000.');
      setLoading(false);
    }
  };

  return (
    <div className="scan-card">
      <div className="scan-label">Enter target URL</div>
      <div className="input-row">
        <div className="input-wrapper">
          <input
            className="url-input"
            type="text"
            placeholder="e.g. example.com"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setTouched(true); }}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleScan()}
            disabled={loading}
            style={{
              borderColor: getBorderColor(),
              boxShadow: getBorderColor()
                ? `0 0 0 3px ${validity ? 'rgba(0,255,136,0.12)' : 'rgba(255,71,87,0.12)'}`
                : undefined
            }}
          />
          {touched && url !== '' && (
            <span className="input-indicator" style={{ color: validity ? 'var(--accent)' : 'var(--danger)' }}>
              {validity ? '✓' : '✗'}
            </span>
          )}
          <div className={`input-helper ${touched && validity === false ? 'error' : ''}`}>
            {touched && validity === false
              ? '✗ Invalid format — try: google.com or https://google.com'
              : 'Enter a domain you own or have permission to scan'}
          </div>
        </div>

        <button
          className={`scan-btn ${loading ? 'scanning' : ''}`}
          onClick={handleScan}
          disabled={loading}
        >
          {loading ? (
            <span className="btn-loading">
              <span className="btn-spinner"></span>
              Scanning...
            </span>
          ) : 'Start Scan'}
        </button>
      </div>
    </div>
  );
}

export default ScanForm;