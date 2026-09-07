import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

export default function TamperResultCard({ tamperData }) {
  if (!tamperData) return null;

  const isFailed = String(tamperData.imageIntegrity || '').toLowerCase().includes('fail') ||
                   String(tamperData.tamperingIndicators || '').toLowerCase().includes('alter') ||
                   String(tamperData.tamperingIndicators || '').toLowerCase().includes('splic');

  const isWarning = !isFailed && (
    String(tamperData.imageIntegrity || '').toLowerCase().includes('warn') ||
    String(tamperData.metadataAnalysis || '').toLowerCase().includes('gimp') ||
    String(tamperData.metadataAnalysis || '').toLowerCase().includes('tool')
  );

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <div
            className="card-icon-box"
            style={{
              background: isFailed ? '#fee2e2' : isWarning ? '#fffbeb' : '#ecfdf5',
              color: isFailed ? '#dc2626' : isWarning ? '#d97706' : '#059669',
            }}
          >
            {isFailed ? <ShieldX size={18} /> : isWarning ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
          </div>
          <div>
            <h3 className="card-title">Tamper Detection Forensics</h3>
            <p className="card-subtitle">Microprinting, photo alteration & metadata signals</p>
          </div>
        </div>

        <span className={`badge ${isFailed ? 'badge-failed' : isWarning ? 'badge-review' : 'badge-verified'}`}>
          <span>{isFailed ? 'Tampering Detected' : isWarning ? 'Anomaly Found' : 'Integrity Valid'}</span>
        </span>
      </div>

      <div className="forensic-field-list">
        <div className="forensic-field-item">
          <span className="field-label">Image Integrity</span>
          <span
            className="field-value"
            style={{ color: isFailed ? 'var(--color-danger)' : isWarning ? 'var(--color-warning)' : 'var(--color-success)' }}
          >
            {tamperData.imageIntegrity || 'Passed'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Metadata Forensics</span>
          <span className="field-value">{tamperData.metadataAnalysis || 'Clean EXIF'}</span>
        </div>

        <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
          <span className="field-label">Tampering Indicators</span>
          <span
            className="field-value"
            style={{ color: isFailed ? 'var(--color-danger)' : isWarning ? 'var(--color-warning)' : 'var(--text-primary)' }}
          >
            {tamperData.tamperingIndicators || 'None'}
          </span>
        </div>

        {tamperData.fontConsistency && (
          <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
            <span className="field-label">Font Consistency & Kerning</span>
            <span className="field-value">{tamperData.fontConsistency}</span>
          </div>
        )}
      </div>
    </div>
  );
}
