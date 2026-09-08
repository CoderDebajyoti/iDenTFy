import React, { useState, useRef } from 'react';
import { UploadCloud, AlertCircle } from 'lucide-react';

const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

export default function FileUpload({ onFileSelect }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const inputRef = useRef(null);

  const validateAndProcessFile = (file) => {
    setErrorMessage(null);

    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setErrorMessage('Unsupported format. Please provide a high-resolution JPG, JPEG, or PNG image.');
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setErrorMessage(`File exceeds 10 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB detected). Please compress or resize.`);
      return;
    }

    // Pass the real browser File object upstream
    onFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div
        className={`dropzone-container ${isDragOver ? 'is-drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        tabIndex={0}
        role="button"
        aria-label="Upload document image"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,image/jpeg,image/png"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <div className="dropzone-icon-circle">
          <UploadCloud size={34} strokeWidth={1.8} />
        </div>

        <div>
          <div className="dropzone-title">Upload Credential Image</div>
          <div className="dropzone-subtitle">
            Drag and drop your scan here, or <span style={{ color: '#2563eb', fontWeight: 600 }}>browse files</span>
          </div>
        </div>

        <div className="dropzone-specs">
          <span className="dropzone-pill">JPG, PNG</span>
          <span className="dropzone-pill">Max 10 MB</span>
          <span className="dropzone-pill">300+ DPI recommended</span>
        </div>
      </div>

      {errorMessage && (
        <div
          style={{
            padding: '12px 16px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: 'var(--radius-md)',
            color: '#991b1b',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.85rem',
          }}
        >
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
