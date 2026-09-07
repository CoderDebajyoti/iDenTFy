import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerification } from '../context/VerificationContext';
import ProcessingSteps from '../components/document/ProcessingSteps';
import { FileText, Scan, Activity } from 'lucide-react';

export default function DocumentProcessing() {
  const navigate = useNavigate();
  const { uploadedFile, filePreviewUrl, startDocumentAnalysis } = useVerification();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // If no file was uploaded, redirect back to upload
  useEffect(() => {
    if (!uploadedFile && !filePreviewUrl) {
      navigate('/verify/document');
    }
  }, [uploadedFile, filePreviewUrl, navigate]);

  // Step progression simulation for pipeline stages
  useEffect(() => {
    let timer;
    if (currentStepIndex < 5) {
      timer = setTimeout(() => {
        setCurrentStepIndex((prev) => prev + 1);
      }, 700);
    } else if (currentStepIndex === 5) {
      timer = setTimeout(async () => {
        await startDocumentAnalysis();
        navigate('/verify/document/result');
      }, 900);
    }
    return () => clearTimeout(timer);
  }, [currentStepIndex, navigate, startDocumentAnalysis]);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Header */}
      <div className="page-header" style={{ textAlign: 'center', marginBottom: '36px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#2563eb', fontWeight: 600, fontSize: '0.85rem', marginBottom: '8px' }}>
          <Activity size={16} className="spin-icon" />
          <span>Screening Pipeline Active</span>
        </div>
        <h1 className="page-title">Analyzing Document...</h1>
        <p className="page-subtitle" style={{ margin: '0 auto' }}>
          Running optical character extraction, document template cross-checking, and digital forensic analysis.
        </p>
      </div>

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
              LIVE SCANNER ACTIVE
            </span>
          </div>

          <div className="scanner-preview-wrapper">
            <div className="scanner-laser-beam" />
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
