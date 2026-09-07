import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import FaceCameraCapture from '../components/face/FaceCameraCapture';
import Button from '../components/common/Button';
import { Lock, ArrowLeft, ShieldAlert } from 'lucide-react';

export default function FaceVerification() {
  const navigate = useNavigate();
  const {
    documentStatus,
    faceStatus,
    submitFaceMatch,
    ocrResult,
  } = useVerification();

  // Guard: Strictly locked if document verification hasn't succeeded
  const isDocumentPassed = documentStatus === 'verified';

  const handleVerifyFace = (blob) => {
    submitFaceMatch(blob);
    navigate('/verify/final');
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
            and database matching.
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

      {/* Face Biometric Camera / Upload Capture Viewport */}
      <FaceCameraCapture
        onVerifyFace={handleVerifyFace}
        currentStatus={faceStatus}
      />
    </div>
  );
}
