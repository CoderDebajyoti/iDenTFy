import React, { useState } from 'react';
import { ScanText, CheckCircle2, Copy, Cpu, ListFilter, Check, AlertCircle } from 'lucide-react';

export default function OCRResultCard({ ocrData, onHoverField }) {
  const [copied, setCopied] = useState(false);
  const [showRawLines, setShowRawLines] = useState(false);

  if (!ocrData) return null;

  const handleCopy = (text) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const confidencePct = Math.round((ocrData.averageConfidence || ocrData.confidence || 0.95) * 100);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="card-header" style={{ marginBottom: 0, paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="card-title-group">
          <div className="card-icon-box" style={{ background: '#eff6ff', color: '#2563eb' }}>
            <ScanText size={18} />
          </div>
          <div>
            <h3 className="card-title">OCR Extracted Data & Tracking</h3>
            <p className="card-subtitle">
              Engine: <strong style={{ color: '#2563eb' }}>{ocrData.engine || 'RapidOCR-ONNX'}</strong> • Optical Confidence: <strong>{confidencePct}%</strong>
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-verified">
            <CheckCircle2 size={13} />
            <span>{ocrData.textLines?.length || 'Live'} Segments</span>
          </span>
        </div>
      </div>

      {/* Forensic Extracted Fields Grid */}
      <div className="forensic-field-list">
        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('name')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Full Name</span>
          <span className="field-value" style={{ fontWeight: 700 }}>
            {ocrData.fullName || '—'}
          </span>
        </div>

        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('doc_num')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Document Number</span>
          <span className="field-value" style={{ color: '#2563eb', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {ocrData.documentNumber || '—'}
          </span>
        </div>

        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('dob')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Date of Birth</span>
          <span className="field-value">{ocrData.dob || '—'}</span>
        </div>

        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('nat')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Nationality</span>
          <span className="field-value" style={{ fontWeight: 600 }}>
            {ocrData.nationality || '—'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Sex / Gender</span>
          <span className="field-value">{ocrData.gender || '—'}</span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Document Type</span>
          <span className="field-value" style={{ textTransform: 'capitalize' }}>
            {(ocrData.documentType || 'passport').replace(/_/g, ' ')}
          </span>
        </div>

        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('issue')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Issue Date</span>
          <span className="field-value">{ocrData.issueDate || '—'}</span>
        </div>

        <div
          className="forensic-field-item"
          onMouseEnter={() => onHoverField && onHoverField('expiry')}
          onMouseLeave={() => onHoverField && onHoverField(null)}
        >
          <span className="field-label">Expiration Date</span>
          <span className="field-value">{ocrData.expiryDate || '—'}</span>
        </div>

        {ocrData.placeOfBirth && (
          <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
            <span className="field-label">Place of Birth</span>
            <span className="field-value">{ocrData.placeOfBirth}</span>
          </div>
        )}

        {ocrData.placeOfIssue && (
          <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
            <span className="field-label">Place of Issue</span>
            <span className="field-value">{ocrData.placeOfIssue}</span>
          </div>
        )}
      </div>

      {/* Machine Readable Zone (MRZ 9303) */}
      {ocrData.mrzRaw && (
        <div style={{ marginTop: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span className="field-label" style={{ marginBottom: 0 }}>Machine Readable Zone (ICAO 9303 MRZ)</span>
            <button
              onClick={() => handleCopy(ocrData.mrzRaw)}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#64748b',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.72rem',
                padding: '2px 6px',
              }}
            >
              {copied ? <Check size={12} style={{ color: '#059669' }} /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy MRZ'}</span>
            </button>
          </div>
          <div
            style={{
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

      {/* Toggle Raw OCR Text Lines Stream */}
      {ocrData.textLines && ocrData.textLines.length > 0 && (
        <div style={{ marginTop: '4px', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
          <button
            onClick={() => setShowRawLines(!showRawLines)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              width: '100%',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              fontSize: '0.8rem',
              fontWeight: 600,
              padding: '4px 0'
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ListFilter size={14} />
              <span>OCR Text Tracking Stream ({ocrData.textLines.length} detected lines)</span>
            </span>
            <span style={{ color: '#2563eb', fontSize: '0.75rem' }}>
              {showRawLines ? 'Hide' : 'Show Details'}
            </span>
          </button>

          {showRawLines && (
            <div
              style={{
                marginTop: '10px',
                maxHeight: '180px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
                padding: '8px',
                background: 'var(--bg-subtle, #f8fafc)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              {ocrData.textLines.map((line, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '4px 8px',
                    background: '#fff',
                    borderRadius: '4px',
                    fontSize: '0.76rem',
                    border: '1px solid #e2e8f0',
                  }}
                >
                  <span style={{ fontFamily: 'var(--font-mono)', color: '#1e293b' }}>
                    {line.text}
                  </span>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      padding: '1px 6px',
                      borderRadius: '10px',
                      backgroundColor: line.confidence >= 0.85 ? '#ecfdf5' : '#fffbeb',
                      color: line.confidence >= 0.85 ? '#059669' : '#d97706',
                    }}
                  >
                    {Math.round(line.confidence * 100)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
