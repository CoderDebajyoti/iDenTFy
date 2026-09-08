import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import FaceCameraCapture from '../components/face/FaceCameraCapture';
import Button from '../components/common/Button';
import { Lock, ArrowLeft, AlertCircle } from 'lucide-react';

export default function FaceVerification() {
  const navigate = useNavigate();
  const {
    documentStatus,
    faceStatus,
    submitFaceMatch,
    ocrResult,
  } = useVerification();
  const [faceError, setFaceError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Strict Security Gate: Strictly locked if document verification hasn't succeeded
  const isDocumentPassed = documentStatus === 'verified';

  const handleVerifyFace = async (blob) => {
    setIsSubmitting(true);
    setFaceError(null);
    const res = await submitFaceMatch(blob);
    setIsSubmitting(false);

    if (res && res.success) {
      navigate('/verify/final');
    } else {
      setFaceError(res?.error || 'Biometric face verification failed to compute match.');
    }
  };

  if (!isDocumentPassed) {
    return (
      <div style={{ maxWidth: '640px', margin: '40px auto', textAlign: 'center' }}>
        <div className="card" style={{ padding: '48px 32px' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: '#fee2e2',
              color: '#dc2626',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 18px',
            }}
          >
            <Lock size={28} />
          </div>

          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-brand-navy)', marginBottom: '10px' }}>
            Face Verification Locked
          </h2>

          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '24px' }}>
            In accordance with security protocol, face verification can only be performed after
            an identity document has successfully passed initial OCR, tampering forensics,
            and database matching. Current document status is:{' '}
            <strong style={{ textTransform: 'uppercase', color: '#dc2626' }}>{documentStatus || 'NOT VERIFIED'}</strong>.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
            <Button
              variant="primary"
              icon={ArrowLeft}
              onClick={() => navigate('/verify/document')}
            >
              Return to Document Verification
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Face Verification</h1>
            <p className="page-subtitle">
              Verify that the physical person matches the identity document portrait ({ocrResult?.fullName || 'Subject'}).
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <Button
              variant="secondary"
              size="sm"
              icon={ArrowLeft}
              onClick={() => navigate('/verify/document/result')}
            >
              Back to Document Result
            </Button>
          </div>
        </div>
      </div>

      {faceError && (
        <div
          style={{
            maxWidth: '800px',
            margin: '0 auto 24px',
            padding: '14px 18px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: 'var(--radius-md)',
            color: '#991b1b',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.88rem',
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{faceError}</span>
        </div>
      )}

      {/* Face Biometric Camera / Upload Capture Viewport */}
      <FaceCameraCapture
        onVerifyFace={handleVerifyFace}
        currentStatus={faceStatus}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
