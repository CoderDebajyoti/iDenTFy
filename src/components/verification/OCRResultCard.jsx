import React from 'react';
import { ScanText, CheckCircle2, Copy } from 'lucide-react';

export default function OCRResultCard({ ocrData }) {
  if (!ocrData) return null;

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon-box">
            <ScanText size={18} />
          </div>
          <div>
            <h3 className="card-title">OCR Extracted Data</h3>
            <p className="card-subtitle">Visual inspection zone & decoded text fields</p>
          </div>
        </div>
        <span className="badge badge-verified">
          <CheckCircle2 size={13} />
          <span>Extracted</span>
        </span>
      </div>

      <div className="forensic-field-list">
        <div className="forensic-field-item">
          <span className="field-label">Full Name</span>
          <span className="field-value">{ocrData.fullName || '—'}</span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Document Number</span>
          <span className="field-value" style={{ color: '#2563eb' }}>
            {ocrData.documentNumber || '—'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Date of Birth</span>
          <span className="field-value">{ocrData.dob || '—'}</span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Nationality</span>
          <span className="field-value">{ocrData.nationality || '—'}</span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Document Type</span>
          <span className="field-value">{ocrData.documentType || '—'}</span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Issue Date</span>
          <span className="field-value">{ocrData.issueDate || '—'}</span>
        </div>

        <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
          <span className="field-label">Expiration Date</span>
          <span className="field-value">{ocrData.expiryDate || '—'}</span>
        </div>
      </div>

      {ocrData.mrzRaw && (
        <div style={{ marginTop: '18px' }}>
          <span className="field-label">Machine Readable Zone (MRZ 9303)</span>
          <div
            style={{
              marginTop: '6px',
              padding: '10px 14px',
              backgroundColor: '#0f172a',
              color: '#38bdf8',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              borderRadius: 'var(--radius-md)',
              letterSpacing: '0.08em',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6',
              border: '1px solid #334155',
            }}
          >
            {ocrData.mrzRaw}
          </div>
        </div>
      )}
    </div>
  );
}
