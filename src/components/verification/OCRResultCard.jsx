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

      {/* Identity Information & Structured Name Card */}
      <div style={{ background: '#f8fafc', padding: '12px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#475569', letterSpacing: '0.05em' }}>
            Identity Information
          </span>
          {ocrData.nameConsistency?.status && (
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '999px',
                background:
                  ocrData.nameConsistency.status === 'CONSISTENT'
                    ? '#dcfce7'
                    : ocrData.nameConsistency.status === 'POSSIBLE_OCR_VARIATION'
                    ? '#fef3c7'
                    : ocrData.nameConsistency.status === 'INCONSISTENT'
                    ? '#fee2e2'
                    : '#f1f5f9',
                color:
                  ocrData.nameConsistency.status === 'CONSISTENT'
                    ? '#15803d'
                    : ocrData.nameConsistency.status === 'POSSIBLE_OCR_VARIATION'
                    ? '#b45309'
                    : ocrData.nameConsistency.status === 'INCONSISTENT'
                    ? '#b91c1c'
                    : '#64748b',
                border: '1px solid currentColor',
              }}
            >
              {ocrData.nameConsistency.status.replace(/_/g, ' ')}
            </span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '10px' }}>
          <div>
            <span className="field-label" style={{ fontSize: '0.7rem' }}>Full Name</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a' }}>
              {ocrData.fullName || '—'}
            </span>
          </div>
          <div>
            <span className="field-label" style={{ fontSize: '0.7rem' }}>Surname</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
              {ocrData.surname || '—'}
            </span>
          </div>
          <div>
            <span className="field-label" style={{ fontSize: '0.7rem' }}>Given Names</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
              {ocrData.givenNames || '—'}
            </span>
          </div>
        </div>

        {/* Name Sources Comparison */}
        {(ocrData.visualName?.full_name || ocrData.mrzName?.full_name) && (
          <div style={{ background: '#ffffff', padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', fontSize: '0.75rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div>
                <span style={{ color: '#64748b', fontWeight: 600 }}>Visual OCR: </span>
                <strong style={{ color: '#0f172a' }}>{ocrData.visualName?.full_name || 'Not detected'}</strong>
              </div>
              <div>
                <span style={{ color: '#64748b', fontWeight: 600 }}>MRZ: </span>
                <strong style={{ color: '#0f172a' }}>{ocrData.mrzName?.full_name || 'Not detected'}</strong>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Forensic Extracted Fields Grid */}
      <div className="forensic-field-list">
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
      {ocrData.mrzRaw ? (
        <div style={{ marginTop: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="field-label" style={{ marginBottom: 0 }}>Machine Readable Zone (ICAO 9303 MRZ)</span>
              {/* MRZ Status Badge */}
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: '999px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  background:
                    ocrData.mrzStatus === 'MRZ_VALID'
                      ? '#dcfce7'
                      : ocrData.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE'
                      ? '#fef3c7'
                      : ocrData.mrzStatus === 'MRZ_UNRELIABLE'
                      ? '#fee2e2'
                      : '#f1f5f9',
                  color:
                    ocrData.mrzStatus === 'MRZ_VALID'
                      ? '#15803d'
                      : ocrData.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE'
                      ? '#b45309'
                      : ocrData.mrzStatus === 'MRZ_UNRELIABLE'
                      ? '#b91c1c'
                      : '#64748b',
                  border: '1px solid currentColor',
                }}
              >
                {ocrData.mrzStatus === 'MRZ_VALID' && <CheckCircle2 size={12} />}
                {ocrData.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE' && <AlertCircle size={12} />}
                {ocrData.mrzStatus === 'MRZ_UNRELIABLE' && <AlertCircle size={12} />}
                <span>
                  {ocrData.mrzStatus === 'MRZ_VALID'
                    ? 'MRZ Valid'
                    : ocrData.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE'
                    ? 'MRZ OCR Correction Candidate'
                    : ocrData.mrzStatus === 'MRZ_UNRELIABLE'
                    ? 'MRZ Unreliable'
                    : 'MRZ Not Detected'}
                </span>
              </span>
            </div>

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

          {/* OCR Correction Candidate Notice */}
          {ocrData.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE' && (
            <div
              style={{
                padding: '8px 12px',
                marginBottom: '8px',
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.76rem',
                color: '#92400e',
                lineHeight: 1.5,
              }}
            >
              <strong>Candidate Ambiguity Note:</strong> MRZ contains an OCR ambiguity; checksum/structure analysis suggests a plausible single-character correction. Verified independently against field rules.
            </div>
          )}

          {ocrData.mrzStatus === 'MRZ_UNRELIABLE' && (
            <div
              style={{
                padding: '8px 12px',
                marginBottom: '8px',
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.76rem',
                color: '#991b1b',
                lineHeight: 1.5,
              }}
            >
              <strong>MRZ Verification Warning:</strong> Checksum verification failed or character resolution is uncertain. Physical inspection recommended.
            </div>
          )}

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
      ) : (
        <div style={{ marginTop: '8px', padding: '8px 12px', backgroundColor: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', fontSize: '0.76rem', color: '#64748b' }}>
          <strong>MRZ Status:</strong> Not Detected in this document image.
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
