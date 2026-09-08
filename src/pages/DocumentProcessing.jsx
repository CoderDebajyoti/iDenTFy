import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import ProcessingSteps from '../components/document/ProcessingSteps';
import Button from '../components/common/Button';
import { FileText, Scan, Activity, AlertCircle, RotateCcw, ArrowLeft } from 'lucide-react';

export default function DocumentProcessing() {
  const navigate = useNavigate();
  const { uploadedFile, filePreviewUrl, startDocumentAnalysis, workflowError } = useVerification();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [localError, setLocalError] = useState(null);
  const hasTriggeredRef = useRef(false);

  // If no file was uploaded, redirect back to upload
  useEffect(() => {
    if (!uploadedFile && !filePreviewUrl) {
      navigate('/verify/document');
    }
  }, [uploadedFile, filePreviewUrl, navigate]);

  // Execute real backend analysis
  const executeAnalysis = async () => {
    setIsAnalyzing(true);
    setLocalError(null);
    setCurrentStepIndex(1);

    // Subtle stage pacing while network request runs
    const stageInterval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < 4 ? prev + 1 : prev));
    }, 600);

    const result = await startDocumentAnalysis();
    clearInterval(stageInterval);
    setIsAnalyzing(false);

    if (result && result.success) {
      setCurrentStepIndex(5);
      // Small visual breath on stage 5 before routing
      setTimeout(() => {
        navigate('/verify/document/result');
      }, 400);
    } else {
      setLocalError(result?.error || 'Document screening pipeline failed to complete.');
    }
  };

  useEffect(() => {
    if (!hasTriggeredRef.current && uploadedFile) {
      hasTriggeredRef.current = true;
      executeAnalysis();
    }
  }, [uploadedFile]);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Header */}
      <div className="page-header" style={{ textAlign: 'center', marginBottom: '36px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: localError ? '#dc2626' : '#2563eb', fontWeight: 600, fontSize: '0.85rem', marginBottom: '8px' }}>
          <Activity size={16} className={isAnalyzing ? 'spin-icon' : ''} />
          <span>{localError ? 'Screening Pipeline Interrupted' : 'Screening Pipeline Active'}</span>
        </div>
        <h1 className="page-title">{localError ? 'Screening Error' : 'Analyzing Document...'}</h1>
        <p className="page-subtitle" style={{ margin: '0 auto' }}>
          {localError
            ? 'The automated screening service encountered an issue processing this document.'
            : 'Running optical character extraction, document template cross-checking, and digital forensic analysis.'}
        </p>
      </div>

      {/* Prominent Error State if Pipeline Fails */}
      {localError && (
        <div
          className="card"
          style={{
            maxWidth: '700px',
            margin: '0 auto 32px',
            padding: '24px',
            border: '1px solid #fca5a5',
            backgroundColor: '#fef2f2',
            boxShadow: 'var(--shadow-md)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#fee2e2',
                color: '#dc2626',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <AlertCircle size={22} />
            </div>

            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#991b1b', marginBottom: '6px' }}>
                Pipeline Execution Failed
              </h3>
              <p style={{ fontSize: '0.88rem', color: '#b91c1c', lineHeight: 1.5, marginBottom: '18px' }}>
                {localError}
              </p>

              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <Button
                  variant="primary"
                  size="sm"
                  icon={RotateCcw}
                  onClick={executeAnalysis}
                >
                  Retry Analysis
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ArrowLeft}
                  onClick={() => navigate('/verify/document')}
                >
                  Return to Document Selection
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Two-column layout: Scanner viewport & Pipeline stages */}
      <div className="processing-layout">
        {/* Central Scanner Preview */}
        <div className="scanner-display-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontSize: '0.85rem', fontWeight: 600 }}>
              <Scan size={16} />
              <span>Optical Sensor Feed</span>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
              {isAnalyzing ? 'LIVE SCANNER ACTIVE' : localError ? 'SENSOR STANDBY' : 'ANALYSIS COMPLETE'}
            </span>
          </div>

          <div className="scanner-preview-wrapper">
            {isAnalyzing && <div className="scanner-laser-beam" />}
            <div className="scanner-grid-overlay" />

            {filePreviewUrl ? (
              <img
                src={filePreviewUrl}
                alt="Document being scanned"
                className="scanner-preview-img"
              />
            ) : (
              <div style={{ color: '#64748b', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                <FileText size={48} />
                <span style={{ fontSize: '0.85rem' }}>Document Buffer Active</span>
              </div>
            )}
          </div>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
            <span>TARGET: {uploadedFile?.name || 'IDENTITY_DOC'}</span>
            <span>FORMAT: {uploadedFile?.type?.toUpperCase() || 'IMAGE'}</span>
          </div>
        </div>

        {/* Processing Stages */}
        <ProcessingSteps currentStepIndex={currentStepIndex} />
      </div>
    </div>
  );
}
