import React, { useState, useEffect } from 'react';
import { checkSystemHealth, API_BASE_URL } from '../services/api';
import Button from '../components/common/Button';
import {
  Server,
  Activity,
  Cpu,
  Shield,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Terminal,
  Settings as SettingsIcon
} from 'lucide-react';

export default function Settings() {
  const [healthResult, setHealthResult] = useState(null);
  const [isPinging, setIsPinging] = useState(false);

  const testPing = async () => {
    setIsPinging(true);
    const start = performance.now();
    const res = await checkSystemHealth();
    const duration = Math.round(performance.now() - start);
    setHealthResult({ ...res, duration });
    setIsPinging(false);
  };

  useEffect(() => {
    testPing();
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">System Settings & Architecture</h1>
            <p className="page-subtitle">
              Inspect application runtime, configure FastAPI endpoint connectivity, and view forensic engine specifications.
            </p>
          </div>

          <div>
            <Button
              variant="secondary"
              size="sm"
              icon={RefreshCw}
              loading={isPinging}
              onClick={testPing}
            >
              Test API Ping
            </Button>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Section 1: API Connection & Infrastructure Probe */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <div className="card-icon-box">
                <Server size={18} />
              </div>
              <div>
                <h3 className="card-title">Backend API Infrastructure</h3>
                <p className="card-subtitle">FastAPI microservice endpoints and live connectivity check</p>
              </div>
            </div>

            {healthResult && (
              <span className={`badge ${healthResult.online ? 'badge-verified' : 'badge-rejected'}`}>
                {healthResult.online ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
                <span>{healthResult.online ? 'Online' : 'Offline'}</span>
              </span>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="forensic-field-list">
              <div className="forensic-field-item">
                <span className="field-label">Target Backend URL</span>
                <span className="field-value" style={{ color: '#2563eb' }}>
                  {API_BASE_URL}
                </span>
              </div>

              <div className="forensic-field-item">
                <span className="field-label">Server Health Endpoint</span>
                <span className="field-value">
                  GET /api/v1/health
                </span>
              </div>

              <div className="forensic-field-item">
                <span className="field-label">Database Connection</span>
                <span className="field-value" style={{ color: healthResult?.database === 'connected' ? '#16a34a' : '#dc2626', fontWeight: 600 }}>
                  {healthResult?.database ? healthResult.database.toUpperCase() : 'CHECKING...'}
                </span>
              </div>

              <div className="forensic-field-item">
                <span className="field-label">Ping Latency</span>
                <span className="field-value">
                  {healthResult?.duration ? `${healthResult.duration} ms` : '—'}
                </span>
              </div>
            </div>

            {healthResult?.error && (
              <div
                style={{
                  padding: '12px 16px',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.82rem',
                  color: '#991b1b',
                  lineHeight: 1.5,
                }}
              >
                <strong>Connection Error:</strong> {healthResult.error}
              </div>
            )}

            <div
              style={{
                padding: '12px 16px',
                backgroundColor: '#f8fafc',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.5,
              }}
            >
              <strong>Technical Infrastructure Notice:</strong> The health probe verifies live network
              connectivity and database responsiveness against <code>/api/v1/health</code>. Verification
              workflows require an active connection to the FastAPI backend service.
            </div>
          </div>
        </div>

        {/* Section 2: Application Information */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#eff6ff', color: '#2563eb' }}>
                <Terminal size={18} />
              </div>
              <div>
                <h3 className="card-title">Application Environment</h3>
                <p className="card-subtitle">Officer workstation and runtime configuration</p>
              </div>
            </div>
          </div>

          <div className="forensic-field-list">
            <div className="forensic-field-item">
              <span className="field-label">System Identity</span>
              <span className="field-value">iDenTFy Console — Ministry of Home Affairs</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">Initiative / Edition</span>
              <span className="field-value">Smart India Hackathon (SIH)</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">Immigration Check Post</span>
              <span className="field-value">ICP-DEL-T3-BOI-04</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">Nodal Authority</span>
              <span className="field-value">Bureau of Immigration, Govt. of India</span>
            </div>
          </div>
        </div>

        {/* Section 3: Forensic & AI Specifications */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#faf5ff', color: '#7c3aed' }}>
                <Cpu size={18} />
              </div>
              <div>
                <h3 className="card-title">Forensic Engine Modules</h3>
                <p className="card-subtitle">Configured computer vision and neural detection models</p>
              </div>
            </div>
          </div>

          <div className="forensic-field-list">
            <div className="forensic-field-item">
              <span className="field-label">OCR & Text Extraction</span>
              <span className="field-value">PaddleOCR Engine v2.7</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">Image Preprocessing</span>
              <span className="field-value">Bilateral Denoising + CLAHE</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">MRZ Parser & Checksums</span>
              <span className="field-value">ICAO 9303 Doc Parser (TD1/TD2/TD3)</span>
            </div>

            <div className="forensic-field-item">
              <span className="field-label">Tamper Forensics</span>
              <span className="field-value">Error Level Analysis (ELA) + Font Kerning</span>
            </div>

            <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
              <span className="field-label">Biometric Verification</span>
              <span className="field-value">1:1 Deep Facial Embedding Vector Cosine Distance</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
