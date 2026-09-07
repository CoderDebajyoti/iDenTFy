import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import RiskMeter from '../components/common/RiskMeter';
import StatusBadge from '../components/common/StatusBadge';
import RiskBadge from '../components/common/RiskBadge';
import Button from '../components/common/Button';
import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Printer,
  RotateCcw,
  History,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  FileText
} from 'lucide-react';

export default function FinalResult() {
  const navigate = useNavigate();
  const {
    finalDecision,
    riskLevel,
    riskScore,
    documentStatus,
    matchingResult,
    tamperResult,
    faceStatus,
    ocrResult,
    verificationId,
    resetWorkflow,
  } = useVerification();

  const isVerified = finalDecision === 'Verified';
  const isReview = finalDecision === 'Requires Review';
  const isFailed = finalDecision === 'Verification Failed';

  const renderIndicator = (statusStr) => {
    const s = String(statusStr || '').toLowerCase();
    if (s.includes('pass') || s.includes('verif') || s.includes('match') && !s.includes('not') && !s.includes('discrep')) {
      return (
        <span style={{ color: 'var(--color-success)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle2 size={18} />
          <span>Passed</span>
        </span>
      );
    }
    if (s.includes('review') || s.includes('warn') || s.includes('discrep') || s.includes('borderline')) {
      return (
        <span style={{ color: 'var(--color-warning)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <AlertTriangle size={18} />
          <span>Requires Review</span>
        </span>
      );
    }
    if (s.includes('fail') || s.includes('not') || s.includes('error')) {
      return (
        <span style={{ color: 'var(--color-danger)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <XCircle size={18} />
          <span>Failed</span>
        </span>
      );
    }
    return (
      <span style={{ color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
        <Clock size={18} />
        <span>Pending</span>
      </span>
    );
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Final Verification Decision</h1>
            <p className="page-subtitle">
              Comprehensive security synthesis for Document #{ocrResult?.documentNumber || 'UNASSIGNED'} ({ocrResult?.fullName || 'Subject'}).
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <Button variant="secondary" size="sm" icon={Printer} onClick={handlePrint}>
              Print Dossier
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={RotateCcw}
              onClick={() => {
                resetWorkflow();
                navigate('/verify/document');
              }}
            >
              New Screening
            </Button>
          </div>
        </div>
      </div>

      {/* Large Status Hero Indicator */}
      <div className="final-decision-hero">
        <div
          style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            backgroundColor: isVerified ? '#ecfdf5' : isReview ? '#fffbeb' : '#fef2f2',
            color: isVerified ? '#059669' : isReview ? '#d97706' : '#dc2626',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          {isVerified ? (
            <ShieldCheck size={40} />
          ) : isReview ? (
            <ShieldAlert size={40} />
          ) : (
            <ShieldX size={40} />
          )}
        </div>

        <div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
            Official Screening Determination
          </span>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-brand-navy)', margin: '4px 0 8px' }}>
            {finalDecision}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', color: '#2563eb' }}>
              Reference: {verificationId || 'IDF-2026-LIVE'}
            </span>
            <span>•</span>
            <RiskBadge level={riskLevel} />
          </div>
        </div>
      </div>

      {/* Risk Meter Gauge */}
      <div style={{ marginBottom: '32px' }}>
        <RiskMeter score={riskScore || (isVerified ? 14 : isReview ? 48 : 92)} level={riskLevel} />
      </div>

      {/* Verification Scorecard Grid */}
      <div style={{ marginBottom: '14px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
          Forensic Scorecard & Factor Breakdown
        </h3>
      </div>

      <div className="final-scorecard-grid">
        {/* Document Status */}
        <div className="scorecard-item">
          <span className="scorecard-label">Document Status</span>
          <div className="scorecard-value">
            {renderIndicator(documentStatus)}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            {ocrResult?.documentType || 'Identity Document'}
          </span>
        </div>

        {/* Database Match */}
        <div className="scorecard-item">
          <span className="scorecard-label">Database Match</span>
          <div className="scorecard-value">
            {renderIndicator(matchingResult?.databaseMatch || 'Pending')}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Registry Cross-Check
          </span>
        </div>

        {/* Tamper Detection */}
        <div className="scorecard-item">
          <span className="scorecard-label">Tamper Forensics</span>
          <div className="scorecard-value">
            {renderIndicator(tamperResult?.imageIntegrity || 'Passed')}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Digital Copy-Paste & ELA
          </span>
        </div>

        {/* Face Verification */}
        <div className="scorecard-item">
          <span className="scorecard-label">Face Biometrics</span>
          <div className="scorecard-value">
            {renderIndicator(faceStatus === 'matched' ? 'Passed' : faceStatus === 'requires_review' ? 'Review' : 'Failed')}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            1:1 Live Subject Match
          </span>
        </div>
      </div>

      {/* Summary Box */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title-group">
            <div className="card-icon-box">
              <FileText size={18} />
            </div>
            <div>
              <h4 className="card-title">Security Officer Summary</h4>
              <p className="card-subtitle">Screening protocol instructions</p>
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {isVerified &&
            'The credential and live biometric capture satisfy all automated validity criteria. Document integrity is intact, MRZ checksums resolve correctly, and registry matching confirmed. Clear to authorize transit/admittance.'}
          {isReview &&
            'Automated screening surfaced discrepancies requiring secondary inspection. An optical anomaly or registry difference was flagged. The officer must physically examine holographic laminate and conduct manual interview.'}
          {isFailed &&
            'CRITICAL SECURITY ALERT: High probability of forged or altered identity credentials. Digital tampering or biometric mismatch detected. Detain credential and escalate to supervisor immediately.'}
        </p>
      </div>

      {/* Bottom Nav Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/history">
          <Button variant="secondary" icon={History}>
            View All Historical Verifications
          </Button>
        </Link>

        <Button
          variant="primary"
          icon={RotateCcw}
          onClick={() => {
            resetWorkflow();
            navigate('/verify/document');
          }}
        >
          Screen Another Document
        </Button>
      </div>
    </div>
  );
}
