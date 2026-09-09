import React, { useState } from 'react';
import { Eye, Layers, Scan, CheckCircle, Crosshair } from 'lucide-react';

export default function DocumentTrackingCard({ previewUrl, textLines = [], highlightedField }) {
  const [showBoxes, setShowBoxes] = useState(true);
  const [hoveredLine, setHoveredLine] = useState(null);

  if (!previewUrl) return null;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div className="card-header" style={{ marginBottom: 0, paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="card-title-group">
          <div className="card-icon-box" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            <Scan size={18} />
          </div>
          <div>
            <h3 className="card-title">Live OCR Document Tracking</h3>
            <p className="card-subtitle">Optical bounding box coordinates & spatial text alignment</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              background: showBoxes ? '#eff6ff' : '#fff',
              color: showBoxes ? '#2563eb' : 'var(--text-secondary)',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <Layers size={13} />
            <span>{showBoxes ? 'Tracking Active' : 'Show Overlay'}</span>
          </button>
        </div>
      </div>

      {/* Interactive Image Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxHeight: '360px',
          overflow: 'hidden',
          borderRadius: 'var(--radius-md)',
          backgroundColor: '#0f172a',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <img
          src={previewUrl}
          alt="Screened Identity Specimen"
          style={{
            maxWidth: '100%',
            maxHeight: '360px',
            objectFit: 'contain',
            display: 'block',
          }}
        />

        {/* Bounding Boxes Layer */}
        {showBoxes && textLines && textLines.length > 0 && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
            }}
          >
            {textLines.map((line, idx) => {
              const nb = line.norm_box;
              if (!nb) return null;
              const isMRZ = line.text?.includes('<') || line.text?.startsWith('P<');
              const isHovered = hoveredLine === idx;

              return (
                <div
                  key={idx}
                  onMouseEnter={() => setHoveredLine(idx)}
                  onMouseLeave={() => setHoveredLine(null)}
                  style={{
                    position: 'absolute',
                    left: `${nb.x}%`,
                    top: `${nb.y}%`,
                    width: `${nb.w}%`,
                    height: `${nb.h}%`,
                    border: isHovered
                      ? '2px solid #38bdf8'
                      : isMRZ
                      ? '1.5px solid rgba(56, 189, 248, 0.85)'
                      : '1.5px solid rgba(34, 197, 94, 0.75)',
                    backgroundColor: isHovered
                      ? 'rgba(56, 189, 248, 0.25)'
                      : isMRZ
                      ? 'rgba(56, 189, 248, 0.12)'
                      : 'rgba(34, 197, 94, 0.08)',
                    borderRadius: '2px',
                    pointerEvents: 'auto',
                    cursor: 'crosshair',
                    transition: 'all 0.15s ease-in-out',
                  }}
                  title={`${line.text} (${Math.round((line.confidence || 0.9) * 100)}%)`}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* OCR Tracking Stats Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
          padding: '6px 4px 0',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Crosshair size={13} style={{ color: '#16a34a' }} />
          <span>{textLines.length} Optical zones mapped with geometry</span>
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: '#64748b' }}>
          ICAO 9303 Compliant Zone Tracking
        </span>
      </div>
    </div>
  );
}
