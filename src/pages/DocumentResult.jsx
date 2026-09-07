import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import StatusBadge from '../components/common/StatusBadge';
import RiskBadge from '../components/common/RiskBadge';
import OCRResultCard from '../components/verification/OCRResultCard';
import MatchingResultCard from '../components/verification/MatchingResultCard';
import TamperResultCard from '../components/verification/TamperResultCard';
import FaceNoticeCard from '../components/verification/FaceNoticeCard';
import Button from '../components/common/Button';
import { RotateCcw, ShieldCheck, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';

export default function DocumentResult() {
  const navigate = useNavigate();
  const {
    documentStatus,
    riskLevel,
    riskScore,
    ocrResult,
    matchingResult,
    tamperResult,
    verificationId,
    resetWorkflow,
  } = useVerification();

  const isDocumentPassed = documentStatus === 'verified';
  const isReview = documentStatus === 'requires_review';
  const isFailed = documentStatus === 'failed' || documentStatus === 'not_verified' || documentStatus === 'error';

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Document Verification Result</h1>
            <p className="page-subtitle">
              Automated optical forensic evaluation, database matching, and metadata validation summary.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <Button
              variant="secondary"
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

      {/* Top Summary Card (Data-Driven) */}
      <div className="result-header-card">
        <div className="result-status-group">
          <div
            className="result-status-icon-box"
            style={{
              backgroundColor: isDocumentPassed ? '#ecfdf5' : isReview ? '#fffbeb' : '#fef2f2',
              color: isDocumentPassed ? '#059669' : isReview ? '#d97706' : '#dc2626',
            }}
          >
            {isDocumentPassed ? (
              <ShieldCheck size={32} />
            ) : isReview ? (
              <AlertTriangle size={32} />
            ) : (
              <XCircle size={32} />
            )}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-brand-navy)' }}>
                Verification Status:
              </h2>
              <StatusBadge status={documentStatus} />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <span>Dossier Ref: <strong style={{ fontFamily: 'var(--font-mono)', color: '#2563eb' }}>{verificationId || 'IDF-LIVE'}</strong></span>
              <span>•</span>
              <span>Processed at: <strong>{new Date().toLocaleTimeString()}</strong></span>
            </div>
          </div>
        </div>

        {/* Risk Level Badge & Score */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Initial Risk Rating:
            </span>
            <RiskBadge level={riskLevel} />
          </div>
          {riskScore !== null && (
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Forensic Risk Score: <strong>{riskScore} / 100</strong>
            </span>
          )}
        </div>
      </div>

      {/* Forensic Analysis Cards Grid */}
      <div className="result-cards-grid">
        <OCRResultCard ocrData={ocrResult} />
        <MatchingResultCard matchingData={matchingResult} />
        <TamperResultCard tamperData={tamperResult} />

        {/* Face Verification Notice (Strictly Pending next step) */}
        <FaceNoticeCard
          isDocumentPassed={isDocumentPassed}
          onProceed={() => navigate('/verify/face')}
        />
      </div>

      {/* Action Footer */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '18px 24px',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
        }}
      >
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isDocumentPassed
            ? 'Document passes initial criteria. Proceeding to face biometric confirmation.'
            : isReview
            ? 'Document flagged for secondary review. Subject must present physical credential.'
            : 'Document failed forgery detection checks. Imposter fraud suspected.'}
        </span>

        {isDocumentPassed && (
          <Button
            variant="primary"
            icon={ArrowRight}
            onClick={() => navigate('/verify/face')}
          >
            Proceed to Face Verification
          </Button>
        )}
      </div>
    </div>
  );
}
