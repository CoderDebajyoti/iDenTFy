import React, { useRef } from 'react';
import { Trash2, RefreshCw, FileText } from 'lucide-react';
import Button from '../common/Button';

export default function DocumentPreview({ file, previewUrl, onRemove, onReplace }) {
  const replaceInputRef = useRef(null);

  if (!file) return null;

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleReplaceChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onReplace(e.target.files[0]);
    }
  };

  return (
    <div className="doc-preview-card">
      <input
        ref={replaceInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        style={{ display: 'none' }}
        onChange={handleReplaceChange}
      />

      <div className="doc-preview-left">
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Document Preview"
            className="doc-thumbnail"
          />
        ) : (
          <div
            className="doc-thumbnail"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
            }}
          >
            <FileText size={28} />
          </div>
        )}

        <div className="doc-preview-info">
          <span className="doc-preview-name" title={file.name}>
            {file.name}
          </span>
          <div className="doc-preview-meta">
            <span>{formatFileSize(file.size)}</span>
            <span>•</span>
            <span style={{ textTransform: 'uppercase' }}>
              {file.type ? file.type.replace('image/', '') : 'IMAGE'}
            </span>
            <span>•</span>
            <span style={{ color: 'var(--color-success)', fontWeight: 600 }}>
              Ready for Analysis
            </span>
          </div>
        </div>
      </div>

      <div className="doc-preview-actions">
        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={() => replaceInputRef.current?.click()}
          title="Replace with another file"
        >
          Replace
        </Button>
        <Button
          variant="danger"
          size="sm"
          icon={Trash2}
          onClick={onRemove}
          title="Remove selected document"
        >
          Remove
        </Button>
      </div>
    </div>
  );
}
