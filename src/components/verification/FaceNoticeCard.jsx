import React from 'react';
import { UserCheck, ArrowRight, Lock } from 'lucide-react';
import Button from '../common/Button';

export default function FaceNoticeCard({ isDocumentPassed, onProceed }) {
  return (
    <div
      className="card"
      style={{
        border: isDocumentPassed ? '1.5px solid #bfdbfe' : '1px solid var(--border-subtle)',
        background: isDocumentPassed ? 'linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%)' : 'var(--bg-surface)',
      }}
    >
      <div className="card-header" style={{ borderBottom: 'none', marginBottom: 0, paddingBottom: 0 }}>
        <div className="card-title-group">
          <div
            className="card-icon-box"
            style={{
              background: isDocumentPassed ? '#eff6ff' : '#f1f5f9',
              color: isDocumentPassed ? '#2563eb' : '#94a3b8',
            }}
          >
            {isDocumentPassed ? <UserCheck size={18} /> : <Lock size={18} />}
          </div>
          <div>
            <h3 className="card-title">Face Verification</h3>
            <p className="card-subtitle">
              {isDocumentPassed
                ? 'Document passed initial validation. Biometric match required to finalize screening.'
                : 'Locked: Document verification must be passed before biometric face comparison can begin.'}
            </p>
          </div>
        </div>

        <div>
          {isDocumentPassed ? (
            <Button variant="primary" icon={ArrowRight} onClick={onProceed}>
              Proceed to Face Verification
            </Button>
          ) : (
            <span className="badge badge-pending">
              <Lock size={12} />
              <span>Pending Pass</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
