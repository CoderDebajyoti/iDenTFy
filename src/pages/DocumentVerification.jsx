import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, FileCheck2 } from 'lucide-react';
import { useVerification } from '../context/VerificationContext';
import DocumentTypeCard from '../components/document/DocumentTypeCard';
import FileUpload from '../components/document/FileUpload';
import DocumentPreview from '../components/document/DocumentPreview';
import Button from '../components/common/Button';

export default function DocumentVerification() {
  const navigate = useNavigate();
  const {
    selectedDocumentType,
    setSelectedDocumentType,
    uploadedFile,
    filePreviewUrl,
    setUploadedFile,
    startDocumentAnalysis,
  } = useVerification();

  const handleAnalyze = async () => {
    if (!uploadedFile) return;
    navigate('/verify/document/processing');
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Document Verification</h1>
            <p className="page-subtitle">
              Upload an identity document to begin automated screening, optical character
              recognition, and forensic forgery analysis.
            </p>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              background: '#ecfdf5',
              border: '1px solid #a7f3d0',
              color: '#065f46',
              fontSize: '0.8rem',
              fontWeight: 600,
            }}
          >
            <ShieldCheck size={16} />
            <span>Encrypted Officer Session</span>
          </div>
        </div>
      </div>

      {/* Step 1: Select Document Type */}
      <section style={{ marginBottom: '32px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
            1. Select Document Credential Type
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Configure optical parsers according to official document template standards
          </p>
        </div>

        <DocumentTypeCard
          selected={selectedDocumentType}
          onSelect={setSelectedDocumentType}
        />
      </section>

      {/* Step 2: Upload Document File */}
      <section style={{ marginBottom: '36px' }}>
        <div style={{ marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
            2. Upload Identity Document Image
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Provide a clear, un-occluded scan or high-resolution photograph of the identity document
          </p>
        </div>

        {!uploadedFile ? (
          <FileUpload onFileSelect={(file) => setUploadedFile(file)} />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <DocumentPreview
              file={uploadedFile}
              previewUrl={filePreviewUrl}
              onRemove={() => setUploadedFile(null)}
              onReplace={(file) => setUploadedFile(file)}
            />

            {/* Prominent Analyze Document Button */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px 22px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <FileCheck2 size={20} style={{ color: '#2563eb' }} />
                <div>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
                    Payload Verified & Ready
                  </span>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    File object stored in memory for transmission to OCR & Forensic engine
                  </p>
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                icon={Sparkles}
                onClick={handleAnalyze}
              >
                Analyze Document
              </Button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
