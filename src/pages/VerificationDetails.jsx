import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getVerificationDetails } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import RiskBadge from '../components/common/RiskBadge';
import RiskMeter from '../components/common/RiskMeter';
import Button from '../components/common/Button';
import {
  ArrowLeft,
  Printer,
  ChevronDown,
  ChevronUp,
  FileText,
  ScanText,
  Database,
  ShieldAlert,
  UserCheck,
  ShieldCheck,
  Calendar,
  Layers,
  FileCheck2
} from 'lucide-react';

export default function VerificationDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);

  // Expandable sections state
  const [expandedSections, setExpandedSections] = useState({
    docInfo: true,
    ocr: true,
    matching: true,
    tamper: true,
    face: true,
    risk: true,
  });

  const [loadError, setLoadError] = useState(null);

  const toggleSection = (key) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      setLoadError(null);
      try {
        const data = await getVerificationDetails(id);
        setRecord(data);
      } catch (err) {
        setLoadError(err.message || 'Failed to retrieve dossier.');
        setRecord(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
        <p>Loading dossier details from database...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '50px 20px', maxWidth: '600px', margin: '40px auto' }}>
        <h3 style={{ color: '#dc2626', marginBottom: '12px' }}>Dossier Service Unavailable</h3>
        <p style={{ color: 'var(--text-muted)', margin: '12px 0 24px', fontSize: '0.9rem' }}>
          {loadError}
        </p>
        <Link to="/history">
          <Button variant="primary" icon={ArrowLeft}>
            Return to Audit History
          </Button>
        </Link>
      </div>
    );
  }

  if (!record) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '50px 20px' }}>
        <h3>Record Not Found</h3>
        <p style={{ color: 'var(--text-muted)', margin: '12px 0 20px' }}>
          No verification dossier found with ID: {id}
        </p>
        <Link to="/history">
          <Button variant="primary" icon={ArrowLeft}>
            Return to Audit History
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1050px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Top Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <Link to="/history">
              <Button variant="secondary" size="sm" icon={ArrowLeft}>
                Back
              </Button>
            </Link>
            <div>
              <h1 className="page-title" style={{ fontSize: '1.5rem' }}>
                Forensic Dossier: <span style={{ fontFamily: 'var(--font-mono)', color: '#2563eb' }}>{record.id}</span>
              </h1>
              <p className="page-subtitle">
                Captured {record.timestamp} • Subject: {record.holderName}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <Button variant="secondary" size="sm" icon={Printer} onClick={() => window.print()}>
              Print Dossier
            </Button>
          </div>
        </div>
      </div>

      {/* Summary Banner */}
      <div className="result-header-card" style={{ marginBottom: '24px' }}>
        <div className="result-status-group">
          <div
            className="result-status-icon-box"
            style={{
              backgroundColor: record.status === 'Verified' ? '#ecfdf5' : record.status.includes('Review') ? '#fffbeb' : '#fef2f2',
              color: record.status === 'Verified' ? '#059669' : record.status.includes('Review') ? '#d97706' : '#dc2626',
            }}
          >
            <ShieldCheck size={30} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-brand-navy)' }}>
                Final Decision: {record.finalDecision || record.status}
              </h3>
              <StatusBadge status={record.status} />
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Official Officer Notes: {record.officerNotes || 'Routine identity screening executed.'}
            </p>
          </div>
        </div>

        <div>
          <RiskBadge level={record.riskLevel} />
        </div>
      </div>

      {/* Accordion / Expandable Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {/* Section 1: Document Information */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.docInfo ? '20px' : 0, borderBottom: expandedSections.docInfo ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('docInfo')}
          >
            <div className="card-title-group">
              <div className="card-icon-box">
                <FileText size={18} />
              </div>
              <div>
                <h3 className="card-title">Document Information</h3>
                <p className="card-subtitle">Credential classification & serial numbers</p>
              </div>
            </div>
            {expandedSections.docInfo ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.docInfo && (
            <div className="forensic-field-list">
              <div className="forensic-field-item">
                <span className="field-label">Document Type</span>
                <span className="field-value">{record.documentType}</span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Document Identifier</span>
                <span className="field-value" style={{ color: '#2563eb' }}>
                  {record.documentNumber}
                </span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Holder Legal Name</span>
                <span className="field-value">{record.holderName}</span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Issuing Authority / Country</span>
                <span className="field-value">{record.nationality}</span>
              </div>
            </div>
          )}
        </div>

        {/* Section 2: OCR Extracted Information */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.ocr ? '20px' : 0, borderBottom: expandedSections.ocr ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('ocr')}
          >
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#eff6ff', color: '#2563eb' }}>
                <ScanText size={18} />
              </div>
              <div>
                <h3 className="card-title">OCR Visual & Machine-Readable Zone</h3>
                <p className="card-subtitle">Parsed text fields & ICAO 9303 MRZ code</p>
              </div>
            </div>
            {expandedSections.ocr ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.ocr && record.ocrDetails && (
            <div>
              {/* Identity Information Section */}
              <div style={{ background: '#f8fafc', padding: '12px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#475569', letterSpacing: '0.05em' }}>
                    Identity Information
                  </span>
                  {record.ocrDetails.nameConsistency?.status && (
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '999px',
                        background:
                          record.ocrDetails.nameConsistency.status === 'CONSISTENT'
                            ? '#dcfce7'
                            : record.ocrDetails.nameConsistency.status === 'POSSIBLE_OCR_VARIATION'
                            ? '#fef3c7'
                            : record.ocrDetails.nameConsistency.status === 'INCONSISTENT'
                            ? '#fee2e2'
                            : '#f1f5f9',
                        color:
                          record.ocrDetails.nameConsistency.status === 'CONSISTENT'
                            ? '#15803d'
                            : record.ocrDetails.nameConsistency.status === 'POSSIBLE_OCR_VARIATION'
                            ? '#b45309'
                            : record.ocrDetails.nameConsistency.status === 'INCONSISTENT'
                            ? '#b91c1c'
                            : '#64748b',
                        border: '1px solid currentColor',
                      }}
                    >
                      {record.ocrDetails.nameConsistency.status.replace(/_/g, ' ')}
                    </span>
                  )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '10px' }}>
                  <div>
                    <span className="field-label" style={{ fontSize: '0.7rem' }}>Full Name</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a' }}>
                      {record.ocrDetails.fullName || '—'}
                    </span>
                  </div>
                  <div>
                    <span className="field-label" style={{ fontSize: '0.7rem' }}>Surname</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                      {record.ocrDetails.surname || '—'}
                    </span>
                  </div>
                  <div>
                    <span className="field-label" style={{ fontSize: '0.7rem' }}>Given Names</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                      {record.ocrDetails.givenNames || '—'}
                    </span>
                  </div>
                </div>

                {/* Name Sources Comparison */}
                {(record.ocrDetails.visualName?.full_name || record.ocrDetails.mrzName?.full_name) && (
                  <div style={{ background: '#ffffff', padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', fontSize: '0.75rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                      <div>
                        <span style={{ color: '#64748b', fontWeight: 600 }}>Visual OCR: </span>
                        <strong style={{ color: '#0f172a' }}>{record.ocrDetails.visualName?.full_name || 'Not detected'}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748b', fontWeight: 600 }}>MRZ: </span>
                        <strong style={{ color: '#0f172a' }}>{record.ocrDetails.mrzName?.full_name || 'Not detected'}</strong>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="forensic-field-list">
                <div className="forensic-field-item">
                  <span className="field-label">Document Number</span>
                  <span className="field-value">{record.ocrDetails.documentNumber}</span>
                </div>
                <div className="forensic-field-item">
                  <span className="field-label">Date of Birth</span>
                  <span className="field-value">{record.ocrDetails.dob}</span>
                </div>
                <div className="forensic-field-item">
                  <span className="field-label">Nationality Code</span>
                  <span className="field-value">{record.ocrDetails.nationality}</span>
                </div>
                <div className="forensic-field-item">
                  <span className="field-label">Issue Date</span>
                  <span className="field-value">{record.ocrDetails.issueDate}</span>
                </div>
                <div className="forensic-field-item">
                  <span className="field-label">Expiry Date</span>
                  <span className="field-value">{record.ocrDetails.expiryDate}</span>
                </div>
              </div>

              {record.ocrDetails.mrzRaw && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span className="field-label" style={{ marginBottom: 0 }}>Raw MRZ Data String (ICAO 9303)</span>
                    {record.ocrDetails.mrzStatus && (
                      <span
                        style={{
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '999px',
                          background:
                            record.ocrDetails.mrzStatus === 'MRZ_VALID'
                              ? '#dcfce7'
                              : record.ocrDetails.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE'
                              ? '#fef3c7'
                              : record.ocrDetails.mrzStatus === 'MRZ_UNRELIABLE'
                              ? '#fee2e2'
                              : '#f1f5f9',
                          color:
                            record.ocrDetails.mrzStatus === 'MRZ_VALID'
                              ? '#15803d'
                              : record.ocrDetails.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE'
                              ? '#b45309'
                              : record.ocrDetails.mrzStatus === 'MRZ_UNRELIABLE'
                              ? '#b91c1c'
                              : '#64748b',
                          border: '1px solid currentColor',
                        }}
                      >
                        {record.ocrDetails.mrzStatus.replace(/_/g, ' ')}
                      </span>
                    )}
                  </div>

                  {record.ocrDetails.mrzStatus === 'MRZ_OCR_CORRECTED_CANDIDATE' && (
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
                      <strong>OCR Correction Candidate:</strong> MRZ contains an OCR ambiguity; checksum/structure analysis identified a plausible single-character candidate.
                    </div>
                  )}

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
                    {record.ocrDetails.mrzRaw}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section 3: Database Matching */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.matching ? '20px' : 0, borderBottom: expandedSections.matching ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('matching')}
          >
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#eef2ff', color: '#4f46e5' }}>
                <Database size={18} />
              </div>
              <div>
                <h3 className="card-title">Database Matching</h3>
                <p className="card-subtitle">Registry lookups and name similarity analysis</p>
              </div>
            </div>
            {expandedSections.matching ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.matching && (
            <div className="forensic-field-list">
              <div className="forensic-field-item">
                <span className="field-label">Central Registry Match</span>
                <span className="field-value">{record.databaseMatch}</span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Visual Field Consistency</span>
                <span className="field-value">
                  {record.status === 'Verified' ? '100% Consistent' : 'Field Discrepancy Found'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Section 4: Tampering Forensics */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.tamper ? '20px' : 0, borderBottom: expandedSections.tamper ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('tamper')}
          >
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#fffbeb', color: '#d97706' }}>
                <ShieldAlert size={18} />
              </div>
              <div>
                <h3 className="card-title">Tampering Analysis & Image Forensics</h3>
                <p className="card-subtitle">Error level analysis (ELA), copy-paste splicing & font kerning</p>
              </div>
            </div>
            {expandedSections.tamper ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.tamper && record.tamperForensics && (
            <div className="forensic-field-list">
              <div className="forensic-field-item">
                <span className="field-label">Image Integrity</span>
                <span className="field-value">{record.tamperForensics.imageIntegrity}</span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Metadata Forensics</span>
                <span className="field-value">{record.tamperForensics.metadataAnalysis}</span>
              </div>
              <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
                <span className="field-label">Tampering Indicators</span>
                <span className="field-value">{record.tamperForensics.tamperingIndicators}</span>
              </div>
              {record.tamperForensics.fontConsistency && (
                <div className="forensic-field-item" style={{ gridColumn: 'span 2' }}>
                  <span className="field-label">Font Consistency</span>
                  <span className="field-value">{record.tamperForensics.fontConsistency}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section 5: Face Verification */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.face ? '20px' : 0, borderBottom: expandedSections.face ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('face')}
          >
            <div className="card-title-group">
              <div className="card-icon-box" style={{ background: '#faf5ff', color: '#7c3aed' }}>
                <UserCheck size={18} />
              </div>
              <div>
                <h3 className="card-title">Face Verification Biometrics</h3>
                <p className="card-subtitle">1:1 facial embedding matching between document portrait & subject</p>
              </div>
            </div>
            {expandedSections.face ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.face && (
            <div className="forensic-field-list">
              <div className="forensic-field-item">
                <span className="field-label">Biometric Match Result</span>
                <span className="field-value">{record.faceVerification}</span>
              </div>
              <div className="forensic-field-item">
                <span className="field-label">Biometric Algorithm</span>
                <span className="field-value">ICAO 9303 Face Embedding v2</span>
              </div>
            </div>
          )}
        </div>

        {/* Section 6: Risk Assessment */}
        <div className="card">
          <div
            className="card-header"
            style={{ cursor: 'pointer', marginBottom: expandedSections.risk ? '20px' : 0, borderBottom: expandedSections.risk ? '1px solid var(--border-subtle)' : 'none' }}
            onClick={() => toggleSection('risk')}
          >
            <div className="card-title-group">
              <div className="card-icon-box">
                <Layers size={18} />
              </div>
              <div>
                <h3 className="card-title">Risk Assessment Summary</h3>
                <p className="card-subtitle">Weighted composite fraud score</p>
              </div>
            </div>
            {expandedSections.risk ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {expandedSections.risk && (
            <RiskMeter score={record.riskScore !== null && record.riskScore !== undefined ? record.riskScore : 0} level={record.riskLevel} />
          )}
        </div>
      </div>
    </div>
  );
}
